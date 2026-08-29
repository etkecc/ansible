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

This role deploys no software. It has no container image, no upstream project and no version of its own — it is a generic mechanism that takes four lists from whoever calls it (directories, files, packages, commands) and applies them to a host. There is nothing to probe over the network, so the suite is written the other way round: it hands the role a representative set of definitions and then reads the host back.

Two things shape almost every assertion:

- **Nothing is asserted merely to exist.** The base directory and one of the files are seeded by `prepare.yml` in a state the role has to *correct* — root-owned at mode `0777`, and a file carrying content the role never wrote at mode `0666`. Every assertion about them is therefore about a change the role made, and a role that only creates what it finds missing cannot pass.
- **There is always something the role was not told about.** A file (`untouched.txt`) sits in the same directory, seeded in the same wrong state, that appears in no definition; a package (`sl`) that no definition names; paths that no definition names. If the role ever started acting on the directory rather than on the lists it was given, these are what would notice.

Ownership carries most of the weight, because the role runs as `root` and everything it creates would come out root-owned if its arguments were dropped. `prepare.yml` creates an unprivileged user and group for exactly that reason, and the mode/owner/group assertions are against those rather than against `root`.

### Defaults are covered from both sides

The role has two layers of defaults — `aux_directory_default_mode` and friends, which a playbook may tune, and the values `defaults/main.yml` ships for them. The scenario covers one layer with each kind of definition:

- **Directories** run with all three defaults set to something *different* from what the role ships (`0710`, and an unprivileged owner and group). That proves those variables actually reach `ansible.builtin.file`.
- **Files** deliberately set none of `aux_file_default_mode`, `aux_file_default_owner` or `aux_file_default_group`. What `verify.yml` asserts there is the value this role *ships* — `0640`, `root`, `root` — spelled out literally rather than read back out of `defaults/main.yml`, which would make the assertion move together with the value it checks. Those defaults decide who can read the files a playbook drops on a server, so changing one is visible to every consumer of this role; this is what makes such a change fail CI instead of landing quietly.

Both ways of feeding the role are exercised too: directories and files are split across the `_auto` and `_custom` halves that `aux_*_definitions` is the sum of, while `aux_command_definitions` is assigned directly, which is the shape [mash-playbook's own documentation](https://github.com/mother-of-all-self-hosting/mash-playbook) shows operators using in `vars.yml`.

### What the suite does not cover

- **Non-Debian hosts.** Both distributions in the CI matrix are Debian-family, so `aux_package_definitions` is only ever exercised through apt. The role uses `ansible.builtin.package`, which picks the host's package manager itself.
- **`aux_package_state`.** Left at the role's default of `present`. Asserting `latest` would mean upgrading whatever the distribution has published since the test image was built.
- **Idempotence.** The scenario leaves the `idempotence` step out of its sequence. `aux_command_definitions` is a list of unconditional commands — one of which is expected to fail every time — so the role reports changes on every run by design.
- **`aux_command_default_become` being set to `true`.** The connection user in the test container is already `root`, so a command that becomes root is indistinguishable from one that does not. The distinction is made the other way round instead: one command becomes an *unprivileged* user and its marker file comes out owned by that user.

## Scenarios

Currently these testing scenarios are available:

### `default`

Everything the role does to a host, in one converge.

It asserts that both halves of `aux_directory_definitions` were applied and that per-item `mode`, `owner` and `group` beat the defaults; that files are rendered with the content they were given byte for byte, at the permissions this role ships, and that an existing file with the wrong content and the wrong permissions is corrected; that a file defined with `src` rather than `content` arrives byte-identical to the fixture on the Ansible controller — the fixture is binary, opening with a NUL byte, because `defaults/main.yml` documents `src` as the way to place content that `content` cannot carry; that the package named in `aux_package_definitions` is installed and its program runs; and that a command with `become_user` really ran as that user, while a command that names no `become` did not.

One command in the scenario is deliberately broken. It removes a file that exists and one that does not, so it does its work and still exits non-zero. The converge surviving it is what proves `ignore_errors` is honored per item, and the removed file being gone afterwards is what proves the command ran at all.

## Running

By default it is configured to run the scenario on Ubuntu 26.04.

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
