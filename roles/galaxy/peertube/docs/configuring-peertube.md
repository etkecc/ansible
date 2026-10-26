<!--
SPDX-FileCopyrightText: 2020 Aaron Raimist
SPDX-FileCopyrightText: 2020 Chris van Dijk
SPDX-FileCopyrightText: 2020 Dominik Zajac
SPDX-FileCopyrightText: 2020 Mickaël Cornière
SPDX-FileCopyrightText: 2020-2024 MDAD project contributors
SPDX-FileCopyrightText: 2020-2024 Slavi Pantaleev
SPDX-FileCopyrightText: 2022 François Darveau
SPDX-FileCopyrightText: 2022 Julian Foad
SPDX-FileCopyrightText: 2022 Warren Bailey
SPDX-FileCopyrightText: 2023 Antonis Christofides
SPDX-FileCopyrightText: 2023 Felix Stupp
SPDX-FileCopyrightText: 2023 Julian-Samuel Gebühr
SPDX-FileCopyrightText: 2023 Pierre 'McFly' Marty
SPDX-FileCopyrightText: 2024 Thomas Miceli
SPDX-FileCopyrightText: 2024 Tiz
SPDX-FileCopyrightText: 2024-2026 Suguru Hirahara

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# Setting up PeerTube

This is an [Ansible](https://www.ansible.com/) role which installs [PeerTube](https://joinpeertube.org/) to run as a [Docker](https://www.docker.com/) container wrapped in a systemd service.

PeerTube is an ActivityPub federated video platform developed by [Framasoft](https://framasoft.org/), a french non-profit.

See the project's [documentation](https://docs.joinpeertube.org/) to learn what PeerTube does and why it might be useful to you.

## Prerequisites

To run a PeerTube instance it is necessary to prepare a [Postgres](https://www.postgresql.org/) database server and [Redis](https://redis.io/) database for managing cache data.

If you are looking for Ansible roles for them, you can check out [ansible-role-postgres](https://github.com/mother-of-all-self-hosting/ansible-role-postgres) and [ansible-role-redis](https://github.com/mother-of-all-self-hosting/ansible-role-redis), both of which are maintained by the [Mother-of-All-Self-Hosting (MASH)](https://github.com/mother-of-all-self-hosting) team. The role for [Valkey](https://valkey.io/) ([ansible-role-valkey](https://github.com/mother-of-all-self-hosting/ansible-role-valkey)) is available as well.

## Adjusting the playbook configuration

To enable PeerTube with this role, add the following configuration to your `vars.yml` file.

**Note**: the path should be something like `inventory/host_vars/mash.example.com/vars.yml` if you use the [MASH Ansible playbook](https://github.com/mother-of-all-self-hosting/mash-playbook).

```yaml
########################################################################
#                                                                      #
# peertube                                                             #
#                                                                      #
########################################################################

peertube_enabled: true

########################################################################
#                                                                      #
# /peertube                                                            #
#                                                                      #
########################################################################
```

### Set the hostname

To enable the PeerTube instance you need to set the hostname as well. To do so, add the following configuration to your `vars.yml` file. Make sure to replace `example.com` with your own value.

```yaml
peertube_hostname: "example.com"
```

After adjusting the hostname, make sure to adjust your DNS records to point the domain to your server.

### Set a random string

You also need to set a random string to the variable as below by adding the following configuration to your `vars.yml` file. The value can be generated with `pwgen -s 64 1` or in another way.

```yaml
peertube_config_secret: YOUR_SECRET_KEY_HERE
```

### Configuring database

#### Set variables for the database server

To have the PeerTube instance connect to your Postgres server, add the following configuration to your `vars.yml` file.

```yaml
peertube_database_username: YOUR_POSTGRES_SERVER_USERNAME_HERE
peertube_database_password: YOUR_POSTGRES_SERVER_PASSWORD_HERE
peertube_database_name: YOUR_POSTGRES_SERVER_DATABASE_NAME_HERE
```

Make sure to replace the placeholders with your own values.

#### Configuring connection to the database server (optional)

By default the role is configured to establish TCP connection with the Postgres server, and you need to add the following configuration to your `vars.yml` file:

```yaml
peertube_database_hostname: YOUR_POSTGRES_SERVER_HOSTNAME_HERE
```

Make sure to replace the placeholders with your own values.

If connection via the Unix socket is preferred, you can mount the Unix socket by adding the following configuration to your `vars.yml` file:

```yaml
# Enable the connection to Postgres server via a Unix socket
peertube_database_socket_enabled: true

# Specify the path to the Postgres Unix socket path on the host (bind-mount source)
peertube_database_socket_path_host: ""
```

### Configure a Redis database

It is necessary to set up a Redis database for the PeerTube instance. Valkey can also be used instead.

To enable the Redis database for PeerTube, add the following configuration to your `vars.yml` file:

```yaml
peertube_redis_hostname: YOUR_REDIS_SERVER_HOSTNAME_HERE
peertube_redis_port: 6379
peertube_redis_username: YOUR_REDIS_SERVER_USERNAME_HERE
peertube_redis_password: YOUR_REDIS_SERVER_PASSWORD_HERE
```

Make sure to replace the placeholders with your own values.

### Set administrator's account details

You also need to specify administrator's account details by adding the following configuration to your `vars.yml` file:

```yaml
peertube_config_admin_email: ADMIN_EMAIL_ADDRESS_HERE
peertube_config_root_user_initial_password: ADMIN_PASSWORD_HERE
```

Generating a strong password (e.g. `pwgen -s 64 1`) is recommended for `peertube_config_root_user_initial_password`.

>[!NOTE]
>
> - The administrator's username is `root`.
> - Subsequent changes to them will not affect the existing user.

### Integrating with Prometheus (optional)

PeerTube can natively expose metrics to Prometheus. If you are looking for an integration, you can check out the MASH Ansible playbook. Please refer to the service's documentation over there for more information.

### Extending the configuration

There are some additional things you may wish to configure about the service.

Take a look at:

- [`defaults/main.yml`](../defaults/main.yml) for some variables that you can customize via your `vars.yml` file. You can override settings (even those that don't have dedicated playbook variables) using the `peertube_environment_variables_additional_variables` variable

## Installing

After configuring the playbook, run the installation command of your playbook as below:

```sh
ansible-playbook -i inventory/hosts setup.yml --tags=setup-all,start
```

If you use the MASH playbook, the shortcut commands with the [`just` program](https://github.com/mother-of-all-self-hosting/mash-playbook/blob/main/docs/just.md) are also available: `just install-all` or `just setup-all`

### Adjust Traefik network's IP address range

After completing the initial installation, it is necessary to adjust the Traefik network's IP address range.

First, find the `traefik` network's IP address range by running the following command on the server: `docker network inspect traefik -f "{{ (index .IPAM.Config 0).Subnet }}"`

Then, add the following configuration after replacing the example IP range below, and re-run the playbook.

```yaml
peertube_trusted_proxies_values_custom: ["172.21.0.0/16"]
```

## Usage

After running the command for installation, PeerTube becomes available at the specified hostname like `https://example.com`.

To get started, open the URL with a web browser to log in to the instance. You should then be able to log in with:

- username: `root`
- password: the password you've set in `peertube_config_root_user_initial_password` in `vars.yml`

## Troubleshooting

### Check the service's logs

You can find the logs in [systemd-journald](https://www.freedesktop.org/software/systemd/man/systemd-journald.service.html) by logging in to the server with SSH and running `journalctl -fu peertube` (or how you/your playbook named the service, e.g. `mash-peertube`).

#### Increase logging verbosity

If you want to increase the verbosity, add the following configuration to your `vars.yml` file:

```yaml
peertube_config_log_level: debug
```

### Upgrading PeerTube

Some PeerTube releases require a migration script to be run by hand once PeerTube has finished its own database migrations (see the *IMPORTANT NOTES* in PeerTube's [CHANGELOG](https://github.com/Chocobozzz/PeerTube/blob/develop/CHANGELOG.md)). When upgrading an existing installation, this role runs these automatically. The scripts it knows about are listed in `peertube_manual_migration_scripts` (in [`vars/main.yml`](vars/main.yml)), which needs to be extended whenever a new PeerTube release introduces one.
