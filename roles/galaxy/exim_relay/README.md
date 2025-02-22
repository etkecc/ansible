<!--
SPDX-FileCopyrightText: 2024 Slavi Pantaleev
SPDX-FileCopyrightText: 2025 Suguru Hirahara

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# exim-relay Ansible role

[![REUSE status](https://api.reuse.software/badge/github.com/mother-of-all-self-hosting/ansible-role-exim-relay)](https://api.reuse.software/info/github.com/mother-of-all-self-hosting/ansible-role-exim-relay)

This is an [Ansible](https://www.ansible.com/) role which installs the [Exim](https://www.exim.org/) mailer via [exim-relay](https://github.com/devture/exim-relay) to run as a [Docker](https://www.docker.com/) container wrapped in a systemd service.

This role *implicitly* depends on:

- [`com.devture.ansible.role.playbook_help`](https://github.com/devture/com.devture.ansible.role.playbook_help)
- [`com.devture.ansible.role.systemd_docker_base`](https://github.com/devture/com.devture.ansible.role.systemd_docker_base)

Check [defaults/main.yml](defaults/main.yml) for the full list of supported options.

For an Ansible playbook which integrates this role and makes it easier to use, see the [mash-playbook](https://github.com/mother-of-all-self-hosting/mash-playbook) or [matrix-docker-ansible-deploy](https://github.com/spantaleev/matrix-docker-ansible-deploy) Ansible playbook.

💡 See this [document](docs/configuring-exim-relay.md) for details about setting up the service with this role.
