<!--
SPDX-FileCopyrightText: 2018-2026 Slavi Pantaleev
SPDX-FileCopyrightText: 2019-2023 MDAD project contributors
SPDX-FileCopyrightText: 2024-2026 Suguru Hirahara
SPDX-FileCopyrightText: 2026 spatterlight

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# Molecule Testing

This role supports [Molecule](https://ansible.readthedocs.io/projects/molecule/), an Ansible testing framework designed for developing and testing Ansible collections, playbooks, and roles.

## Prerequisites

To utilize Molecule you need to prepare several requirements:

- **x86** computer running one of these operating systems:
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

## What the suite can and cannot tell you

Read this before changing anything under `molecule/`. Swap is a property of the kernel, and a container shares its kernel with the machine running the tests. A `swapon`, `swapoff` or `sysctl` that succeeded in a container would act on that machine.

- All scenarios run **unprivileged** containers with **no systemd**, where none of the three can work. `prepare.yml` asserts this before it does anything else. Never make a platform privileged.
- `prepare.yml` puts recording shims in front of the three tools, in `/usr/local/sbin`, so that the role can finish and `verify.yml` can check what it asked for.
- `prepare.yml` refuses to run if a scenario's swap files add up to more than 128 MB, because they are written to a real disk.

A green run proves what the role wrote to disk (the swap files, `/etc/fstab`, `/etc/sysctl.d/99-swap.conf`), what it asked the three tools for, and that a second run changes nothing. It does not prove that the swap is usable or that the kernel accepts the parameter values, as neither reaches the kernel. `verify.yml` asserts instead that the kernel's own list of swap areas came through unchanged.

The `default` and `uninstall` scenarios run the role twice in `converge.yml` instead of using Molecule's `idempotence` step, which would fail because `ansible.posix.sysctl` reports a change on every reload. The `file-removal` scenario sets no kernel parameters and keeps the step.

## Scenarios

Currently these testing scenarios are available:

### `default`

`system_swap_enabled: true` on a host with no swap, for two swap files: one described by `system_swap_path`, `system_swap_size` and `system_swap_priority`, the other added through `system_swap_files_custom` with no priority.

Every value differs from the role's own default, and what `verify.yml` expects of each swap file is spelled out by hand in `molecule.yml` rather than read back out of `system_swap_files`. A decoy file the role was never told about must be left untouched.

### `uninstall`

`system_swap_enabled: false` on a host with three swap files, of which two are in `system_swap_files`. Both must be gone afterwards, from disk and from `/etc/fstab`, and the third must be left alone.

The scenario also asserts that `/etc/sysctl.d/99-swap.conf` is left behind, which the role does on purpose.

### `file-removal`

`system_swap_enabled: true` on a host with three swap files: one to keep, one marked `state: absent` and one the role was never told about. The role is also asked for a new swap file.

Afterwards only the marked one may be gone, and the new one must be in place. Both shims write to a single log, so that `verify.yml` can assert the new swap file was enabled before the old one was disabled.

## Running

By default it is configured to run the scenarios on Ubuntu 26.04.

```bash
molecule test --scenario-name default
```

You can utilize other distributions by setting one to the `MOLECULE_DISTRO` environment variable:

```bash
# Debian 13
MOLECULE_DISTRO=debian13 molecule test --scenario-name uninstall

# Debian 12
MOLECULE_DISTRO=debian12 molecule test --scenario-name default
```
