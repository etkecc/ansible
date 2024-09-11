# Postgres-backup Ansible role

This is an [Ansible](https://www.ansible.com/) role which sets up [prodrigestivill/docker-postgres-backup-local](https://github.com/prodrigestivill/docker-postgres-backup-local) for backing up [Postgres](https://www.postgresql.org/) (no matter if it's installed via [com.devture.ansible.role.postgres](https://github.com/devture/com.devture.ansible.role.postgres/) or not).

The `postgres-backup` service is installed to run as a [Docker](https://www.docker.com/) container wrapped in a systemd service.

This role *implicitly* depends on:

- [`com.devture.ansible.role.playbook_help`](https://github.com/devture/com.devture.ansible.role.playbook_help)
- [`com.devture.ansible.role.systemd_docker_base`](https://github.com/devture/com.devture.ansible.role.systemd_docker_base)


## Usage

Example playbook:

```yaml
- hosts: servers
  roles:
    - role: galaxy/com.devture.ansible.role.systemd_docker_base

    - role: galaxy/com.devture.ansible.role.postgres_backup

    - role: another_role
```

Example playbook configuration (`group_vars/servers` or other):

```yaml
devture_postgres_backup_identifier: my-postgres-backup

devture_postgres_backup_architecture: amd64

devture_postgres_base_path: "{{ my_base_path }}/postgres-backup"

devture_postgres_backup_container_network: "{{ my_container_container_network }}"

devture_postgres_backup_uid: "{{ my_uid }}"
devture_postgres_backup_gid: "{{ my_gid }}"

devture_postgres_backup_connection_hostname: ""
devture_postgres_backup_connection_username: ""
devture_postgres_backup_connection_password: ""

# If Postgres is running on the same machine, set this to its data path,
# so the Postgres version will be autodetected.
devture_postgres_backup_postgres_data_path: ""
# Alternatively, you'd need to configure `devture_postgres_backup_container_image_to_use`.

devture_postgres_backup_databases: ['first', 'second', 'third']
```
