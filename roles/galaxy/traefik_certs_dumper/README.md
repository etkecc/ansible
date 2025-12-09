<!--
SPDX-FileCopyrightText: 2023 Slavi Pantaleev

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# Traefik certs dumper Ansible role

This is an [Ansible](https://www.ansible.com/) role which installs [traefik-certs-dumper](https://github.com/ldez/traefik-certs-dumper) to run as a [Docker](https://www.docker.com/) container wrapped in a systemd service.

This role *implicitly* depends on [`com.devture.ansible.role.systemd_docker_base`](https://github.com/devture/com.devture.ansible.role.systemd_docker_base).

This role is related to the [mother-of-all-self-hosting/ansible-role-traefik](https://github.com/mother-of-all-self-hosting/ansible-role-traefik) role and integrates nicely with it, but using them both together is **not** a requirement.

💡 See this [document](docs/configuring-traefik-certs-dumper.md) for details about setting up the service with this role.

## Development

You can optionally install [pre-commit](https://pre-commit.com/) so that simple mistakes are checked and noticed before changes are pushed to a remote branch. See [`.pre-commit-config.yaml`](./.pre-commit-config.yaml) for which hooks are to be executed.

See [this section](https://pre-commit.com/#usage) on the official documentation for usage.
