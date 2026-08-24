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

Tests a standard linkding installation on SQLite.

Beyond the systemd service being active, it checks that linkding reports itself healthy on `/health` — the one endpoint that opens a database connection — that the version it reports and the version file inside the image both match `linkding_version`, that the environment file the role rendered reached the process, that the superuser the role was asked to create exists and that its password authenticates (and that a wrong one does not), and that a bookmark written through the REST API can be read back through the API and is found in the database and in the SQLite file on the host.

### `default-selfbuild`

Tests a standard linkding installation with self-building the container image.

It proves the running container was built here rather than pulled — the role tags a self-built image `v<version>`, which upstream never publishes, and a built image carries no registry digest. This scenario also deliberately configures no superuser, which is the case the other two do not cover: it asserts that no superuser variables reach the environment and that linkding creates no account at all.

### `postgres`

Tests a standard linkding installation with the Postgres database.

A scenario named after a backend is no proof that the application ended up using it — linkding falls back to SQLite whenever `LD_DB_ENGINE` does not say otherwise — so this one reads the backend off the connection Django actually opened, and then looks for the bookmark it wrote through the API in the Postgres database itself, with `psql`.

### What these scenarios deliberately do not gate on

linkding is a Django application, and its login page renders without ever touching the database. A container pointed at a nonexistent database host still answers `/` with a `302` and `/login/` with a `200`, with uWSGI up and every migration failed. Asserting on either would pass on a completely broken installation, so the scenarios gate on `/health` instead, which calls `ensure_connection()` and answers `500` when the database is unreachable.

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
