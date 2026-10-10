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

## What the suite can and cannot tell you

This role deploys no software. It installs no container, starts no service of its own and has no upstream project behind it — it is host-level housekeeping, and most of what it does is destructive. So there is nothing to probe over the network here, and the suite is instead written around the line between what the role removes and what it must leave alone. Both sides of that line are seeded before the role runs, and both are asserted afterwards; a suite that only checked the removals would pass just as happily against a role that deleted everything.

Where the role renders configuration — the journald autovacuum units — the values are read back out of `systemctl show` rather than off the disk, so what is asserted is systemd's own parse of the unit, and every value the scenario sets is deliberately different from the role's own default so that a template which ignored its variables could not look correct.

What the suite does not cover:

- **`system_cleanup_apt`'s upgrade step.** The scenario sets `system_cleanup_apt_upgrade_type` to `no`, because an actual `safe` upgrade would download whatever the distribution has published since the test image was built. What is asserted is the second half of `tasks/run_apt.yml`: a file seeded into `/var/cache/apt/archives` is gone afterwards, which only `apt-get clean` could have done.
- **`purge-old-kernels` actually purging a kernel.** A container has no kernel packages, and the scenario asserts `/boot` is empty precisely so that running the script there is known to be a no-op. What is asserted is that the script the role vendors was installed at the configured path, at the configured mode, byte for byte, and runs.
- **The grace period.** An image's arrival time (`LastTagTime`) cannot be backdated, and every image in the scenario is minutes old, so the scenario sets the grace period to 0 days and asserts the rule itself: an unused image is removed only if a newer image of its repository exists.
- **Idempotence.** The role is not idempotent and is not meant to be: it starts a `Type=oneshot` unit that has gone back to inactive by the next run, and its pruning and package-manager tasks are unconditional commands. Both scenarios therefore leave the `idempotence` step out of their test sequence.

## Scenarios

Currently these testing scenarios are available:

### `default`

Everything the role does to a host except Docker pruning and most of the uninstalling.

It asserts that the journald autovacuum service and timer are installed, that systemd parsed them with this scenario's retention and schedule rather than the role's defaults, that the timer is enabled and active and that the service ran and reported vacuuming the journals; that the two paths named in `system_cleanup_paths` are gone while two identically seeded neighbours which were *not* named are untouched; that the apt archive cache was emptied; and that `purge-old-kernels` was installed at the path `system_cleanup_kernels_script` names — and nowhere near the role's default path.

The scenario also runs with `system_cleanup_docker` turned on, on a host that has no Docker at all. The role's Docker pruning is tagged `start`, and this scenario skips that tag (`--skip-tags start`), so the pruning tasks are skipped. Had the gate stopped working, `docker container prune` would have run and the converge would have failed on `docker: command not found`. The Docker cleanup timer is left off, and stand-ins for its units, installed and enabled before the role runs, are asserted to be stopped, disabled and removed afterwards.

### `default-docker`

The destructive half: `system_cleanup_docker` with the `start` tag actually present, which is how [mash-playbook](https://github.com/mother-of-all-self-hosting/mash-playbook) invokes the role (`--tags=setup-all,start`). The role's files are moved to a non-default base path, and the cleanup script is asserted to be installed there. The scenario also turns on the optional removal of anonymous volumes, and the timer (under a non-default identifier and schedule), whose units are read back out of systemd.

It also covers the role uninstalling what it no longer should have: `system_cleanup_logs` and `system_cleanup_kernels` are off, and stand-ins for the journald autovacuum units (installed and enabled) and for `purge-old-kernels` (at the role's path and at `/usr/local/bin`, where earlier versions of the role installed it), put in place before the role runs, are asserted to be stopped, disabled and removed afterwards.

An empty Docker daemon is filled with a running container, a stopped one, the image the running container uses, an unused image which is the only one of its repository, two unused images of another repository (one superseded by the other), a named volume in use, an unused named volume, an anonymous volume nothing references any more, and a network attached to nothing. After the role has run, the stopped container, the superseded image and the anonymous volume are gone, and everything else — including the contents of the volume in use — is still there.

Three of those are worth spelling out:

- **The unused image without a newer version is preserved.** This is what sets the role apart from `docker image prune -a`: it stands for the image of a stopped service, or of a container that only runs on a timer.

- **Networks are preserved.** The role runs no `docker network prune`, which `defaults/main.yml` promises. The network seeded here is attached to nothing, so a prune would take it.
- **Unused *named* volumes are preserved.** Since Docker 23, `docker volume prune` without `--all` removes only anonymous volumes, and the role passes no `--all`. This is asserted deliberately: a named volume is where a self-hosted service keeps its data.

## Running

By default it is configured to run the scenarios on Ubuntu 26.04.

```bash
molecule test --scenario-name default
```

You can utilize other distributions by setting one to the `MOLECULE_DISTRO` environment variable:

```bash
# Debian 13
MOLECULE_DISTRO=debian13 molecule test --scenario-name default

# Debian 12
MOLECULE_DISTRO=debian12 molecule test --scenario-name default
```

Note that `tasks/run_apt.yml` and `tasks/run_kernels.yml` only run on Debian-family hosts, so a scenario run against another distribution family exercises less of the role.
