<!--
SPDX-FileCopyrightText: 2026 Suguru Hirahara
-->

# Postgres Ansible role

This is an [Ansible](https://www.ansible.com/) role which installs [Postgres](https://www.postgresql.org/) to run as a [Docker](https://www.docker.com/) container wrapped in a systemd service.

This role *implicitly* depends on:

- [`com.devture.ansible.role.playbook_help`](https://github.com/devture/com.devture.ansible.role.playbook_help)
- [`com.devture.ansible.role.systemd_docker_base`](https://github.com/devture/com.devture.ansible.role.systemd_docker_base)

Check [`defaults/main.yml`](defaults/main.yml) for the full list of supported options.

💡 For an Ansible playbook which integrates this role and makes it easier to use, see the [Mother-of-All-Self-Hosting Ansible playbook](https://github.com/mother-of-all-self-hosting/mash-playbook).

## Features

- **multiple databases support**: this role manages one main database and root credentials, and optionally a list of additional managed databases with their own credentials (see `postgres_managed_databases`)

- **backward compatible**: even if a new Postgres version is available, the role will keep you on the Postgres version you had started with until you perform a major upgrade manually (see below)

- **upgrading between major Postgres versions**: invoking the playbook with a `--tags=upgrade-postgres` performs a dump, data move (`data` -> `data-auto-upgrade-backup`), rebuild, and dump import

- **importing existing Postgres database dumps**: you can import plain-text (`.sql`), gzipped (`sql.gz`), zstandard-compressed (`.sql.zst`) dumps with the `--tags=import-postgres` tag

- **import data from SQLite, NeDB, etc**: this is an internal task (not exposed as a playbook tag), but the role supports using [pgloader](https://pgloader.io/) to load data into Postgres

- **vacuum support**: you can vacuum all configured databases in one run using the `--tags=run-postgres-vacuum` tag

- **helpful scripts**:
  - get a `psql` interactive terminal via the `/base_path/bin/cli` and `/base_path/bin/cli-non-interactive` scripts
  - dump all databases using the `/base_path/bin/dump-all DIRECTORY_PATH` (which will dump to a `latest-dump.sql.gz` file there)

## Usage

Example playbook:

```yaml
- hosts: servers
  roles:
    - role: galaxy/com.devture.ansible.role.systemd_docker_base

    - role: galaxy/postgres

    - role: another_role
```

Example playbook configuration (`group_vars/servers` or other):

```yaml
postgres_identifier: my-postgres

postgres_base_path: "{{ my_base_path }}/postgres"

postgres_container_network: "{{ my_container_container_network }}"

postgres_uid: "{{ my_uid }}"
postgres_gid: "{{ my_gid }}"

postgres_vacuum_default_databases_list: ["mydb", "anotherdb"]

postgres_systemd_services_to_stop_for_maintenance_list: |
  {{
    (['my-service.service'])
  }}

postgres_managed_databases: |
  {{
    [{
      'name': my_database_name,
      'username': my_database_username,
      'password': my_database_password,
    }]
    +
    [{
      'name': another_database_name,
      'username': another_database_username,
      'password': another_database_password,
    }]
  }}
```

## Development

You can optionally install [pre-commit](https://pre-commit.com/) so that simple mistakes are checked and noticed before changes are pushed to a remote branch. See [`.pre-commit-config.yaml`](./.pre-commit-config.yaml) for which hooks are to be executed.

See [this section](https://pre-commit.com/#usage) on the official documentation for usage.
