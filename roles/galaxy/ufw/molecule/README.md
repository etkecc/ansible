<!--
SPDX-FileCopyrightText: 2018-2025 Slavi Pantaleev
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
> This role reconfigures the firewall of the host it runs against. The scenarios below always run it against a throwaway Docker container, never against your machine. A Docker container has its own network namespace, so `ufw enable` inside it programs netfilter rules that apply to that container alone; your host's firewall and every other container are left alone. Do not point these scenarios at a host you care about.

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

Starts from a container with no firewall at all — `prepare.yml` asserts that ufw is not installed — and lets the role install it, add rules drawn from all three rule lists (`system_security_ufw_rules_base`, `system_security_ufw_rules_auto` and `system_security_ufw_rules_custom`), and bring the firewall up.

Verification reads both `ufw status verbose` (what ufw has recorded) and `iptables-save` (what the kernel is enforcing), and checks both directions: every configured rule has to be there, and ports that were never configured — including ufw's conventional `22/tcp`, which is absent only because the role honors `system_security_ssh_port` — must not be.

### `rule-removal`

The opposite direction. `prepare.yml` brings ufw up with `2222/tcp` and `19999/tcp` already open, and asserts that they really are, so that the removals verified later cannot be mistaken for rules that were simply never added.

The role then runs with `system_security_ufw_ssh_allowed: false` and with a custom rule carrying `delete: true`, and verification checks that both rules are gone from ufw and from the kernel, while the base rules are still in place.

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
