#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Slavi Pantaleev
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Probes a running Uptime Kuma over its Socket.IO API and reports what it finds.

Usage: probe-uptime-kuma.py <base-url> <username> <password>

Uptime Kuma is a single-page application whose HTTP surface cannot be trusted
to say anything about the server behind it: every path, including paths that do
not exist, answers 200 with the same 2.4KB application shell. An unconfigured
instance, a fully configured one and an unrelated static site are
indistinguishable over plain HTTP.

Everything that can actually be verified lives behind Socket.IO, so this script
speaks it directly over its HTTP long-polling transport (no third-party client
library, no WebSocket upgrade needed):

- a fresh instance emits a `setup` event on connect, which is what tells a
  server that has never been configured apart from one that has
- the `setup` event completes the setup wizard, creating the admin user. That
  write goes into the SQLite database under `/app/data`, which is the directory
  this role bind-mounts and chowns, so it fails if the mount or its ownership
  is wrong
- logging in as that admin returns a session token
- only an *authenticated* connection is told the version. Uptime Kuma sends
  `info` with the version field omitted to anonymous sockets, so the running
  version simply cannot be read without completing the two steps above

The resulting `info` payload reports the running server's own version, its
timezone and whether it was told it is containerized -- values that the caller
asserts against the role's variables.

Prints a JSON report on stdout and exits non-zero if the probe could not be
completed.
"""

import json
import sys
import time
import urllib.error
import urllib.request

# Long polls are held open by the server until it has something to say, up to
# its ping interval (25s by default).
POLL_TIMEOUT_SECONDS = 40

# How long to keep retrying the initial handshake while the server boots.
HANDSHAKE_TIMEOUT_SECONDS = 120


class ProbeError(Exception):
    pass


class SocketIOClient:
    """A minimal Socket.IO (Engine.IO v4) client speaking the polling transport.

    Only one poll may be in flight at a time: Engine.IO closes the session when
    it sees overlapping GET requests from the same client, so every request here
    is issued strictly sequentially.
    """

    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")
        self.session_id = None
        self.next_ack_id = 0
        self.received_events = []

    def _request(self, url, body=None):
        headers = {"Content-Type": "text/plain;charset=UTF-8"} if body else {}
        request = urllib.request.Request(url, data=body, headers=headers)
        with urllib.request.urlopen(request, timeout=POLL_TIMEOUT_SECONDS) as response:
            return response.read().decode("utf-8", "replace")

    def _polling_url(self, **params):
        query = "EIO=4&transport=polling"
        if self.session_id:
            query += "&sid=" + self.session_id
        for name, value in params.items():
            query += "&{}={}".format(name, value)
        return "{}/socket.io/?{}".format(self.base_url, query)

    def connect(self):
        deadline = time.monotonic() + HANDSHAKE_TIMEOUT_SECONDS
        last_error = None

        while time.monotonic() < deadline:
            try:
                handshake = self._request(self._polling_url(t="handshake"))
                self.session_id = json.loads(handshake[1:])["sid"]
                break
            except (urllib.error.URLError, OSError, ValueError, KeyError) as error:
                last_error = error
                time.sleep(3)
        else:
            raise ProbeError("Socket.IO handshake never succeeded: {}".format(last_error))

        # Connect to the default namespace.
        self._request(self._polling_url(), b"40")

    def poll(self):
        """Reads one batch of packets, recording events and answering pings."""
        payload = self._request(self._polling_url(t="poll"))
        packets = payload.split("\x1e")

        for packet in packets:
            if packet == "2":
                # Engine.IO ping. Answering keeps the session from being reaped.
                self._request(self._polling_url(), b"3")
            elif packet.startswith("42") or packet.startswith("43"):
                self.received_events.append(packet)

        return packets

    def emit(self, event_name, *args):
        """Sends an event with an acknowledgement id and returns that id."""
        self.next_ack_id += 1
        ack_id = self.next_ack_id
        packet = "42{}{}".format(ack_id, json.dumps([event_name, *args]))
        self._request(self._polling_url(), packet.encode("utf-8"))
        return ack_id

    def _decode(self, packet):
        """Turns a `42["name", ...]` or `43N[...]` packet into its payload list."""
        body = packet[2:]
        while body and body[0].isdigit():
            body = body[1:]
        try:
            return json.loads(body)
        except ValueError:
            return None

    def wait_for_ack(self, ack_id, attempts=6):
        prefix = "43{}[".format(ack_id)
        for _ in range(attempts):
            for packet in self.received_events:
                if packet.startswith(prefix):
                    decoded = self._decode(packet)
                    return decoded[0] if decoded else None
            self.poll()
        raise ProbeError("No acknowledgement for request {}".format(ack_id))

    def wait_for_event(self, event_name, predicate=None, attempts=6):
        for _ in range(attempts):
            for packet in self.received_events:
                if not packet.startswith("42"):
                    continue
                decoded = self._decode(packet)
                if not decoded or decoded[0] != event_name:
                    continue
                payload = decoded[1] if len(decoded) > 1 else None
                if predicate is None or predicate(payload):
                    return payload
            self.poll()
        raise ProbeError("Never received a matching '{}' event".format(event_name))

    def has_event(self, event_name):
        for packet in self.received_events:
            if packet.startswith("42"):
                decoded = self._decode(packet)
                if decoded and decoded[0] == event_name:
                    return True
        return False


def probe(base_url, username, password):
    client = SocketIOClient(base_url)
    client.connect()

    # Drain what the server volunteers on connect. A never-configured instance
    # announces itself with a `setup` event here.
    client.poll()
    setup_offered = client.has_event("setup")

    setup_result = client.wait_for_ack(client.emit("setup", username, password))
    setup_completed = bool(setup_result and setup_result.get("ok"))

    # Re-running the probe against an instance a previous run configured is a
    # legitimate outcome, and is not the same thing as setup having failed.
    already_configured = bool(
        setup_result
        and not setup_result.get("ok")
        and "has been initialized" in setup_result.get("msg", "")
    )

    if not (setup_completed or already_configured):
        raise ProbeError("Setup was refused: {}".format(setup_result))

    login_result = client.wait_for_ack(
        client.emit("login", {"username": username, "password": password, "token": ""})
    )

    if not (login_result and login_result.get("ok")):
        raise ProbeError("Login was refused: {}".format(login_result))

    # Anonymous connections get an `info` without a version, so wait for the one
    # sent to the now-authenticated socket rather than whichever came first.
    info = client.wait_for_event(
        "info", predicate=lambda payload: bool(payload) and payload.get("version")
    )

    return {
        "ok": True,
        "setup_offered": setup_offered,
        "setup_completed": setup_completed,
        "already_configured": already_configured,
        "login_ok": True,
        "token_returned": bool(login_result.get("token")),
        "info": info,
    }


def main():
    if len(sys.argv) != 4:
        print(json.dumps({"ok": False, "error": __doc__.splitlines()[2]}))
        return 2

    base_url, username, password = sys.argv[1:4]

    try:
        report = probe(base_url, username, password)
    except (ProbeError, urllib.error.URLError, OSError, ValueError) as error:
        print(json.dumps({"ok": False, "error": "{}: {}".format(type(error).__name__, error)}))
        return 1

    print(json.dumps(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
