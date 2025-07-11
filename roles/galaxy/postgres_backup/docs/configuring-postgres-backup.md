<!--
SPDX-FileCopyrightText: 2021 foxcris
SPDX-FileCopyrightText: 2021 - 2024 Slavi Pantaleev
SPDX-FileCopyrightText: 2024 - 2025 Suguru Hirahara

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# Setting up Postgres backup

This is an [Ansible](https://www.ansible.com/) role which sets up [prodrigestivill/docker-postgres-backup-local](https://github.com/prodrigestivill/docker-postgres-backup-local) for backing up [Postgres](https://www.postgresql.org/).

For a more complete backup solution (one that includes not only Postgres, but also other configuration/data files), you may wish to look into [BorgBackup](https://github.com/mother-of-all-self-hosting/ansible-role-backup_borg) instead.

## Adjusting the playbook configuration

To enable Postgres backup with this role, add the following configuration to your `vars.yml` file.

**Note**: the path should be something like `inventory/host_vars/matrix.example.com/vars.yml` if you use the [matrix-docker-ansible-deploy (MDAD)](https://github.com/spantaleev/matrix-docker-ansible-deploy) or [Mother-of-All-Self-Hosting (MASH)](https://github.com/mother-of-all-self-hosting/mash-playbook) Ansible playbook.

```yaml
########################################################################
#                                                                      #
# postgres-backup                                                      #
#                                                                      #
########################################################################

postgres_backup_enabled: true

########################################################################
#                                                                      #
# /postgres-backup                                                     #
#                                                                      #
########################################################################
```

Refer to the table below for additional configuration variables and their default values.

| Name                              | Default value                | Description                                                      |
| :-------------------------------- | :--------------------------- | :--------------------------------------------------------------- |
|`postgres_backup_enabled`|`false`|Set to true to use [docker-postgres-backup-local](https://github.com/prodrigestivill/docker-postgres-backup-local) to create automatic database backups|
|`postgres_backup_schedule`| `'@daily'` |Cron-schedule specifying the interval between Postgres backups.|
|`postgres_backup_keep_days`|`7`|Number of daily backups to keep|
|`postgres_backup_keep_weeks`|`4`|Number of weekly backups to keep|
|`postgres_backup_keep_months`|`12`|Number of monthly backups to keep|
|`postgres_backup_base_path` | `"{{ matrix_base_data_path }}/postgres-backup"` | Base path for postgres-backup. Also see `postgres_backup_data_path` |
|`postgres_backup_data_path` | `"{{ postgres_backup_base_path }}/data"` | Storage path for postgres-backup database backups |

### Extending the configuration

There are some additional things you may wish to configure about the component.

Take a look at:

- [`defaults/main.yml`](../defaults/main.yml) for some variables that you can customize via your `vars.yml` file

## Installing

After configuring the playbook, run the installation command of your playbook as below:

```sh
ansible-playbook -i inventory/hosts setup.yml --tags=setup-all,start
```

If you use the MDAD / MASH playbook, the shortcut commands with the [`just` program](https://github.com/spantaleev/matrix-docker-ansible-deploy/blob/master/docs/just.md) are also available: `just install-all` or `just setup-all`

## Troubleshooting

You can find the logs in [systemd-journald](https://www.freedesktop.org/software/systemd/man/systemd-journald.service.html) by logging in to the server with SSH and running `journalctl -fu postgres-backup` (or how you/your playbook named the service, e.g. `matrix-postgres-backup`).
