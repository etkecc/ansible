<!--
SPDX-FileCopyrightText: 2023-2025 Slavi Pantaleev
SPDX-FileCopyrightText: 2026 Suguru Hirahara

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# Docker Socket Proxy Ansible role

This is an [Ansible](https://www.ansible.com/) role which installs [Docker Socket Proxy](https://github.com/Tecnativa/docker-socket-proxy) to run as a [Docker](https://www.docker.com/) container wrapped in a systemd service.

This role *implicitly* depends on the [`com.devture.ansible.role.systemd_docker_base` role](https://github.com/devture/com.devture.ansible.role.systemd_docker_base).

May be used in combination with the [`ansible-role-traefik` role](https://github.com/mother-of-all-self-hosting/ansible-role-traefik).

💡 For an Ansible playbook which integrates this role and makes it easier to use, see the [Mother-of-All-Self-Hosting Ansible playbook](https://github.com/mother-of-all-self-hosting/mash-playbook).

## Development

You can optionally install [pre-commit](https://pre-commit.com/) so that simple mistakes are checked and noticed before changes are pushed to a remote branch. See [`.pre-commit-config.yaml`](./.pre-commit-config.yaml) for which hooks are to be executed.

See [this section](https://pre-commit.com/#usage) on the official documentation for usage.
