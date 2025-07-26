<!--
SPDX-FileCopyrightText: 2023 Julian-Samuel Gebühr
SPDX-FileCopyrightText: 2023 Slavi Pantaleev
SPDX-FileCopyrightText: 2025 Suguru Hirahara

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# Funkwhale Ansible role

This is an [Ansible](https://www.ansible.com/) role which installs [Funkwhale](https://funkwhale.audio/) to run as a [Docker](https://www.docker.com/) container wrapped in a systemd service.

This role *implicitly* depends on:

- [`com.devture.ansible.role.playbook_help`](https://github.com/devture/com.devture.ansible.role.playbook_help)
- [`com.devture.ansible.role.systemd_docker_base`](https://github.com/devture/com.devture.ansible.role.systemd_docker_base)

## Usage

If you wish to boost the performance of your pod, you can try tweaking these variables:

- `funkwhale_frontend_web_workers`: increase to allow more parallel connections of web workers
- `funkwhale_celery_worker_concurrency`: increase the number of worker processes for background tasks
