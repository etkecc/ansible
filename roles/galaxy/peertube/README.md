<!--
SPDX-FileCopyrightText: 2023, 2026 Slavi Pantaleev
SPDX-FileCopyrightText: 2026 Suguru Hirahara

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# PeerTube Ansible role

This is an [Ansible](https://www.ansible.com/) role which installs [PeerTube](https://joinpeertube.org/) to run as a [Docker](https://www.docker.com/) container wrapped in a systemd service.

This role *implicitly* depends on:

- [`com.devture.ansible.role.playbook_help`](https://github.com/devture/com.devture.ansible.role.playbook_help)
- [`com.devture.ansible.role.systemd_docker_base`](https://github.com/devture/com.devture.ansible.role.systemd_docker_base)

Check [`defaults/main.yml`](defaults/main.yml) for the full list of supported options.

💡 For an Ansible playbook which integrates this role and makes it easier to use, see the [Mother-of-All-Self-Hosting Ansible playbook](https://github.com/mother-of-all-self-hosting/mash-playbook).

## Upgrading PeerTube

`peertube_version` names a PeerTube release (`v8.3.0`), which is also the container image tag (see `peertube_container_image_tag`). Since 8.0.0, PeerTube publishes plain version tags; the Debian-flavoured ones (`v8.3.0-trixie`) are deprecated upstream, and Renovate (see [`.github/renovate.json`](.github/renovate.json)) ignores them.

Some PeerTube releases require a migration script to be run by hand once PeerTube has finished its own database migrations (see the *IMPORTANT NOTES* in PeerTube's [CHANGELOG](https://github.com/Chocobozzz/PeerTube/blob/develop/CHANGELOG.md)). When upgrading an existing installation, this role runs these automatically. The scripts it knows about are listed in `peertube_manual_migration_scripts` (in [`vars/main.yml`](vars/main.yml)), which needs to be extended whenever a new PeerTube release introduces one.

Version bumps are never automerged here: PeerTube runs its database migrations unattended on startup, and its patch releases do carry them.

## Releases

Tags are cut automatically by [`.github/workflows/autotag.yml`](.github/workflows/autotag.yml), from the state of the repository rather than from commit messages. [`bin/compute-next-tag.sh`](bin/compute-next-tag.sh) reads `peertube_version` out of [`defaults/main.yml`](defaults/main.yml) and the tags that already exist:

- a PeerTube version that has never been released starts the release counter at 0 (`v7.3.0-0`)
- any other change under `defaults/`, `meta/`, `tasks/`, `templates/` or `vars/` increments it (`v7.3.0-1`)
- changes that do not affect what a playbook run does (README, CI configuration, Molecule tests) release nothing

[`bin/test-compute-next-tag.sh`](bin/test-compute-next-tag.sh) exercises that against throwaway repositories, and runs as a prek hook whenever those scripts or `defaults/main.yml` change.

## Development

### pre-commit

You can optionally install a Git pre-commit hook (via [mise](https://mise.jdx.dev/) + [prek](https://prek.j178.dev/)) that runs formatting and linting checks before each commit. See [`.pre-commit-config.yaml`](./.pre-commit-config.yaml) for which hooks are to be executed.

To install the hook, run the [`just`](https://github.com/casey/just) command below:

```sh
just prek-install-git-pre-commit-hook
```

### Molecule

This role supports [Molecule](https://docs.ansible.com/projects/molecule/), an Ansible testing framework designed for developing and testing Ansible collections, playbooks, and roles.

Refer to [this page](./molecule/README.md) for details about how to utilize it.
