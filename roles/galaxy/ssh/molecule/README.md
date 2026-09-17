<!--
SPDX-FileCopyrightText: 2018-2026 Slavi Pantaleev
SPDX-FileCopyrightText: 2019-2023 MDAD project contributors
SPDX-FileCopyrightText: 2024-2026 Suguru Hirahara

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# Molecule Testing

This role supports [Molecule](https://ansible.readthedocs.io/projects/molecule/), an Ansible testing framework designed for developing and testing Ansible collections, playbooks, and roles.

## Prerequisites

To utilize Molecule you need to prepare several requirements:

- **x86** computer running one of these operating systems that make use of [systemd](https://systemd.io/):
  - **Archlinux**
  - **CentOS**, **Rocky Linux**, **AlmaLinux**, or possibly other RHEL alternatives (although your mileage may vary)
  - **Debian** (10/Buster or newer)
  - **Ubuntu** (18.04 or newer)
- `root` access on the computer which Molecule runs against
- [Ansible](http://ansible.com/) program
- [Python](https://www.python.org/)
- [Docker](https://www.docker.com)
  - Access to Docker UNIX socket (`/var/run/docker.sock`) is required by default

## Installation

To set up the environment for using Molecule, run the command below on the terminal:

```bash
python3 -m venv ./molecule/venv
source ./molecule/venv/bin/activate
pip3 install -r ./molecule/requirements.txt
```

## A warning before you run any of this

This role rewrites `/etc/ssh/sshd_config` and reloads the SSH daemon. Pointed at the wrong machine, that is how an operator locks themselves out of their own server.

Every playbook in this suite therefore begins by asserting that `/.dockerenv` exists and refuses to go any further if it does not. Keep that guard. It is the only thing standing between `molecule converge` and somebody's production `sshd`.

## What the suite can and cannot tell you

This role deploys no software. It installs no container and starts no service of its own — it configures the OpenSSH server the host already runs, and there is no upstream project behind it whose version could be asserted. So there is nothing to probe over the network in the usual sense, and the suite is instead built in three layers, each closer to reality than the last:

1. **The file on disk is the role's, not the distribution's.** `prepare.yml` appends a marker to the stock `sshd_config`; the role renders the whole file from its template, so the marker's absence afterwards — together with the `ansible_managed` header — says the file was replaced rather than edited.
2. **sshd's own parse of it carries this scenario's values.** Assertions compare against `sshd -T`, which is what sshd itself makes of the file, so a directive sshd ignores or a later line overrides cannot pass. Every value the scenario sets is deliberately different from **both** the role's default **and** the value the distribution ships, and each assertion also states that the role's default is *absent*. `prepare.yml` proves the "before" side of that by reading the stock configuration back through `sshd -T` and refusing to continue if any of the scenario's values is already in effect — without that, an assertion like "sshd listens on port 2022" could pass against a role that did nothing.
3. **A real SSH daemon answers on the port the role asked for.** This is the only part that the role's reload step has to have run for. `sshd -T` reads the file and would be just as happy if the running daemon had never heard of it; connecting to the port and reading an `SSH-2.0-` banner off it would not.

Values are also asserted in the *unsafe* direction where the role allows it — `X11Forwarding` and `AllowTcpForwarding` are turned **on** in the `default` scenario, against role defaults of `false`. A template that hardcoded the hardened answer would pass a suite that only ever checked for `no`.

The two backward-compatibility paths in `defaults/main.yml` are covered as behavior rather than as comments: `system_security_ssh_passwordauth` (the older name that `system_security_ssh_password_authentication` derives from) is the only password-authentication variable the `default` scenario sets, and `system_security_ssh_permit_root_login_raw` is set to something that contradicts the boolean so that the documented precedence between them can only pass if the raw value wins.

What the suite does **not** cover:

- Distributions outside the Debian family. Both test images are Debian-derived, which is what lets `prepare.yml` install `openssh-server` with `apt`. The role itself claims Archlinux and EL support in `meta/main.yml`.
- The `sshd` → `ssh` fall-through in `system_security_ssh_services`. Both test images resolve `sshd.service`, so the first candidate always wins. On Debian the alias is created by `systemctl enable ssh.service` and disabling the unit removes it, but a Debian host with `ssh.service` disabled *and* `ssh.socket` in charge is exactly the host the role cannot reload (see below), so there is no arrangement in which the fall-through can be exercised end to end here.
- Upgrades. Every run is a fresh install onto a stock `sshd_config`.

## The scenarios

### `default`

A host in the classic arrangement: `sshd` owns its own listening socket, `ssh.socket` is stopped and disabled. This is what Debian ships and what most existing servers look like.

It is the scenario that can prove the role end to end, because on such a host the `Port` directive really does move the daemon. `prepare.yml` leaves a stock daemon answering on 22 and nothing on 2022; `verify.yml` finds the SSH protocol on 2022 and port 22 closed.

### `socket-activated`

A host in the arrangement Ubuntu 24.04 and newer ship by default: `ssh.socket` holds the listening socket and hands it to `sshd`, which is started on demand.

This scenario exists to pin down a real limitation. **On a socket-activated host, `system_security_ssh_port` does nothing.** The port comes from `ssh.socket`'s `ListenStream=`, and `sshd` is handed that socket; the `Port` line the role writes into `sshd_config` is simply ignored. The scenario sets the port to 2022, asserts that `sshd_config` says so, and then asserts that the daemon is still answering on 22 — deliberately, so that whoever eventually teaches the role about socket units has to come here and change this file on purpose.

The assertion is not vacuous: the same run proves the role's configuration *did* reach `sshd` (`MaxAuthTries`, `PermitRootLogin`, the deliberately omitted `PerSourceMaxStartups`), so "the port did not change" cannot be explained away by the role having done nothing at all.

It also asserts that the reload left a working daemon behind, which on such a host is not a given. Reloading `sshd` sends it a `SIGHUP`, on which it re-executes and re-binds. On Ubuntu (OpenSSH 9.6 on 24.04, 10.2 on 26.04) it quietly keeps the socket it was handed. On **Debian 13** (OpenSSH 10.0) the same re-exec ends in `fatal: Cannot bind any address`, the unit exits 255, and `RestartPreventExitStatus=255` stops systemd from bringing it back — the role's `Reload SSH daemon` task fails and the playbook aborts. Debian does not enable `ssh.socket` by default, so this only bites hosts where somebody turned it on; the daemon returns on the next inbound connection through the socket, so it is a failed run rather than a lockout. It is not asserted here, because a green test that encodes "the role breaks" reads to everyone else as "this is fine".

### Running them

```bash
molecule test --scenario-name default
MOLECULE_DISTRO=debian13 molecule test --scenario-name default
molecule test --scenario-name socket-activated
```

`socket-activated` is written for the Ubuntu image and CI runs it there only; `default` runs on both.
