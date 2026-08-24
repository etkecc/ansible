<!--
SPDX-FileCopyrightText: 2018-2026 Slavi Pantaleev
SPDX-FileCopyrightText: 2019-2022 Aaron Raimist
SPDX-FileCopyrightText: 2019-2023 MDAD project contributors
SPDX-FileCopyrightText: 2023 QEDeD
SPDX-FileCopyrightText: 2024 Fabio Bonelli
SPDX-FileCopyrightText: 2024 Nikita Chernyi
SPDX-FileCopyrightText: 2024-2026 Suguru Hirahara
SPDX-FileCopyrightText: 2026 spatterlight

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# Molecule Testing

This role supports [Molecule](https://docs.ansible.com/projects/molecule/), an Ansible testing framework designed for developing and testing Ansible collections, playbooks, and roles.

> [!IMPORTANT]
> This role installs an intrusion-prevention daemon on the host it runs against and lets it program that host's firewall. The scenarios below always run it against a throwaway Docker container, never against your machine. A Docker container has its own network namespace, so the nftables rules fail2ban installs inside it apply to that container alone; your host's firewall and every other container are left alone. Do not point these scenarios at a host you care about.

## Prerequisites

To utilize Molecule you need to prepare several requirements:

- **x86** computer running one of these operating systems that make use of [systemd](https://systemd.io/):
  - **Archlinux**
  - **CentOS**, **Rocky Linux**, **AlmaLinux**, or possibly other RHEL alternatives (although your mileage may vary)
  - **Debian** (10/Buster or newer)
  - **Ubuntu** (18.04 or newer, although [20.04 may be problematic](https://github.com/mother-of-all-self-hosting/mash-playbook/blob/main/docs/ansible.md#supported-ansible-versions) if you run the Ansible playbook on it)
- `root` access on the computer which Molecule runs against
- [Ansible](http://ansible.com/) program
- [Python](https://www.python.org/)
  - Most distributions install Python by default, but some don't (e.g. Ubuntu 18.04) and require manual installation (something like `apt-get install python3`)
- [Docker](https://www.docker.com)
  - Access to Docker UNIX socket (`/var/run/docker.sock`) is required by default

## Installation

To set up the environment for using Molecule, run the command below on the terminal:

```bash
python3 -m venv ./molecule/venv
source ./molecule/venv/bin/activate
pip3 install -r ./molecule/requirements.txt
```

## Scenarios

Currently these testing scenarios are available:

### `default`

Starts from a container with no intrusion prevention at all — `prepare.yml` asserts that fail2ban is not installed — and lets the role install it, write `jail.local` and start the daemon.

Verification does not stop at "the unit is active", which `Restart=always` would say about a daemon in a crash loop and which is true of a `fail2ban-server` whose jails have all failed to start. Instead it asks the running server, over its own socket, what it understood: which jails it started, which port the `sshd` jail bans on, which addresses it ignores, and whether ban-time escalation is on.

It then provokes a real ban. `system_security_fail2ban_configuration_extension` adds a jail that runs fail2ban's stock `sshd` filter against a log file the scenario writes to (the `sshd` jail itself reads the systemd journal, whose `_SYSTEMD_UNIT` and `_COMM` fields are set by systemd and cannot be forged from a playbook). Failures are written for two addresses: one ordinary, and one listed in `system_security_fail2ban_ignoreip`.

The result is read from two places that can disagree — `fail2ban-client status`, which is fail2ban's own bookkeeping, and `nft --json list ruleset`, which is what the kernel will actually enforce. A banning action that silently failed would show up as a ban in the first and nothing in the second. The ignored address, which took exactly the same failures through exactly the same jail, has to be absent from both, as does an address that never failed anything.

### `disabled`

The other direction. `prepare.yml` installs fail2ban, stops it and writes a `jail.local` of its own, and asserts that the file is really there — so that "the role did not write jail.local" cannot be confused with a file that was never going to exist.

The role then runs with `system_security_fail2ban_enabled: false`, and verification checks that the foreign `jail.local` survived byte for byte, that no `fail2ban-server` is answering, and that the unit is not active.

## Running

By default it is configured to run the scenarios on Ubuntu 26.04.

```bash
molecule test --scenario-name default
```

You can utilize other distributions by setting one to the `MOLECULE_DISTRO` environment variable:

```bash
# Ubuntu 24.04
MOLECULE_DISTRO=ubuntu2404 molecule test --scenario-name default

# Debian 13
MOLECULE_DISTRO=debian13 molecule test --scenario-name default

# Debian 12
MOLECULE_DISTRO=debian12 molecule test --scenario-name default
```
