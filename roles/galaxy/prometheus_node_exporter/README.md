<!--
SPDX-FileCopyrightText: 2023 Nikita Chernyi

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# prometheus_node_exporter

This is an [Ansible](https://www.ansible.com/) role which installs [Prometheus node exporter](https://github.com/prometheus/node_exporter) to run as a [Docker](https://www.docker.com/) container wrapped in a systemd service.

This role *implicitly* depends on:

- [`com.devture.ansible.role.playbook_help`](https://github.com/devture/com.devture.ansible.role.playbook_help)
- [`com.devture.ansible.role.systemd_docker_base`](https://github.com/devture/com.devture.ansible.role.systemd_docker_base)

> **NOTE**: check [defaults/main.yml](./defaults/main.yml) to see full list of config options

## Development

You can optionally install [pre-commit](https://pre-commit.com/) so that simple mistakes are checked and noticed before changes are pushed to a remote branch. See [`.pre-commit-config.yaml`](./.pre-commit-config.yaml) for which hooks are to be executed.

See [this section](https://pre-commit.com/#usage) on the official documentation for usage.
