<!--
SPDX-FileCopyrightText: 2023 kinduff

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# linkding Ansible role

This is an [Ansible](https://www.ansible.com) role which installs [linkding](https://github.com/sissbruecker/linkding) to run as a [Docker](https://www.docker.com) container wrapped in a systemd service.

This role _implicitly_ depends on:

- [`com.devture.ansible.role.playbook_help`](https://github.com/devture/com.devture.ansible.role.playbook_help)
- [`com.devture.ansible.role.systemd_docker_base`](https://github.com/devture/com.devture.ansible.role.systemd_docker_base)

Check [defaults/main.yml](defaults/main.yml) for the full list of supported options.

---

Thanks for the work of [etke.cc](https://gitlab.com/etke.cc/) for the template for this role.
