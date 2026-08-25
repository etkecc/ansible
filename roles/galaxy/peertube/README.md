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

`peertube_version` names a PeerTube release (`v7.2.3`), and `peertube_container_image_tag` composes the container image tag out of it and `peertube_distro_variant`.

PeerTube published its 6.x and 7.x images only under Debian-flavoured tags (`v7.2.3-bookworm`, with no plain `v7.2.3` alongside them), and deprecated that suffix in 8.0.0, where `v8.2.4` is the tag to use and `v8.2.4-trixie` merely still exists. Renovate is configured (in [`.github/renovate.json`](.github/renovate.json)) to read versions out of the `-bookworm` tags, which is the namespace this role installs from, so **moving to 8.x means changing `peertube_distro_variant` and that rule together**. 8.0.0 additionally asks for a migration script to be run by hand once the upgrade is done — see PeerTube's [8.0.0 release notes](https://github.com/Chocobozzz/PeerTube/releases/tag/v8.0.0).

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
