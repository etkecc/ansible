# SPDX-FileCopyrightText: 2026 Slavi Pantaleev
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Sends nginx access-log lines to prometheus-nginxlog-exporter over syslog.

The role's default configuration takes its input from a syslog listener
rather than from a log file, so this is how an access log reaches the
exporter in production: nginx is pointed at a syslog target, and the
exporter parses what arrives.

Each datagram is an RFC 3164 message whose content is one nginx access-log
line in the format the role templates. The exporter keeps only the messages
whose syslog tag matches the one it was configured with, so the tag is
passed in rather than assumed.

Invoked as `python3 seed-syslog-lines.py ...`, so it deliberately carries no
shebang and needs no execute bit.
"""

import argparse
import socket
import time


def build_log_line(args, timestamp):
    """One access-log line in the role's templated format.

    The format the role ships is, with the Nginx variables spelled out:

        log_source server_name - upstream_addr - remote_addr - remote_user
        [time_local] host "request" status "http_referer" "http_user_agent"
        "http_x_forwarded_for"

    A line that does not match it is counted as a parse error instead of a
    request, which is why verify.yml asserts that the parse error counter
    stayed at zero.
    """
    return (
        '{log_source} {server_name} - {upstream_addr} - {remote_addr} - {remote_user} '
        '[{timestamp}] {server_name} "{method} {request_uri} HTTP/1.1" {status} '
        '"-" "{user_agent}" "-"'
    ).format(
        log_source=args.log_source,
        server_name=args.server_name,
        upstream_addr=args.upstream_addr,
        remote_addr=args.remote_addr,
        remote_user=args.remote_user,
        timestamp=timestamp,
        method=args.method,
        request_uri=args.request_uri,
        status=args.status,
        user_agent=args.user_agent,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, required=True)
    parser.add_argument('--tag', required=True, help='syslog tag the exporter filters on')
    parser.add_argument('--count', type=int, required=True)
    parser.add_argument('--status', required=True)
    parser.add_argument('--request-uri', required=True)
    parser.add_argument('--server-name', required=True)
    parser.add_argument('--remote-addr', required=True)
    parser.add_argument('--method', default='GET')
    parser.add_argument('--log-source', default='molecule')
    parser.add_argument('--upstream-addr', default='10.0.0.5:8080')
    parser.add_argument('--remote-user', default='molecule')
    parser.add_argument('--user-agent', default='molecule-seeder/1.0')
    args = parser.parse_args()

    now = time.gmtime()
    # The nginx `time_local` format. The exporter does not turn this into a
    # metric - the role's format captures no request duration or byte count -
    # so it only has to be shaped like the real thing.
    log_timestamp = time.strftime('%d/%b/%Y:%H:%M:%S +0000', now)
    # The RFC 3164 header. `<190>` is local7.info, which is what nginx's
    # `access_log syslog:...` emits by default.
    syslog_header = '<190>{} molecule {}:'.format(
        time.strftime('%b %d %H:%M:%S', now), args.tag
    )

    message = '{} {}'.format(syslog_header, build_log_line(args, log_timestamp))
    payload = message.encode('utf-8')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        for _ in range(args.count):
            sock.sendto(payload, (args.host, args.port))
            # Datagrams are handed to a single reader goroutine inside the
            # exporter. Spacing them out keeps this from depending on how
            # deep that reader's queue happens to be.
            time.sleep(0.1)
    finally:
        sock.close()

    print('Sent {} syslog datagram(s) to {}:{} with tag {}'.format(
        args.count, args.host, args.port, args.tag
    ))
    print(message)


if __name__ == '__main__':
    main()
