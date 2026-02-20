<!--
SPDX-FileCopyrightText: 2022-2024 Slavi Pantaleev
SPDX-FileCopyrightText: 2026 Suguru Hirahara

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# Postgres-backup Ansible role

[![REUSE status](https://api.reuse.software/badge/github.com/mother-of-all-self-hosting/ansible-role-postgres-backup)](https://api.reuse.software/info/github.com/mother-of-all-self-hosting/ansible-role-postgres-backup)

This is an [Ansible](https://www.ansible.com/) role which sets up [prodrigestivill/docker-postgres-backup-local](https://github.com/prodrigestivill/docker-postgres-backup-local) for backing up [Postgres](https://www.postgresql.org/) (no matter if it's installed via [mother-of-all-self-hosting/ansible-role-postgres](https://github.com/mother-of-all-self-hosting/ansible-role-postgres) or not).

The `postgres-backup` service is installed to run as a [Docker](https://www.docker.com/) container wrapped in a systemd service.

This role *implicitly* depends on:

- [`com.devture.ansible.role.playbook_help`](https://github.com/devture/com.devture.ansible.role.playbook_help)
- [`com.devture.ansible.role.systemd_docker_base`](https://github.com/devture/com.devture.ansible.role.systemd_docker_base)

## Usage

💡 Refer to [this page](docs/configuring-postgres-backup.md) for details about setting up the service with this role.

Example playbook:

```yaml
- hosts: servers
  roles:
    - role: galaxy/com.devture.ansible.role.systemd_docker_base

    - role: galaxy/postgres_backup

    - role: another_role
```

Example playbook configuration (`group_vars/servers` or other):

```yaml
postgres_backup_identifier: my-postgres-backup

postgres_backup_architecture: amd64

postgres_backup_base_path: "{{ my_base_path }}/postgres-backup"

postgres_backup_container_network: "{{ my_container_container_network }}"

postgres_backup_uid: "{{ my_uid }}"
postgres_backup_gid: "{{ my_gid }}"

postgres_backup_connection_hostname: ""
postgres_backup_connection_username: ""
postgres_backup_connection_password: ""

# If Postgres is running on the same machine, set this to its data path,
# so the Postgres version will be autodetected.
postgres_backup_postgres_data_path: ""
# Alternatively, you'd need to configure `postgres_backup_container_image_to_use`.

postgres_backup_databases_auto: ['first', 'second', 'third']
```

## Development

You can optionally install [pre-commit](https://pre-commit.com/) so that simple mistakes are checked and noticed before changes are pushed to a remote branch. See [`.pre-commit-config.yaml`](./.pre-commit-config.yaml) for which hooks are to be executed.

See [this section](https://pre-commit.com/#usage) on the official documentation for usage.
