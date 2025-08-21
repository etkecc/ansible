<!--
SPDX-FileCopyrightText: 2020 - 2024 MDAD project contributors
SPDX-FileCopyrightText: 2020 - 2024 Slavi Pantaleev
SPDX-FileCopyrightText: 2020 Aaron Raimist
SPDX-FileCopyrightText: 2020 Chris van Dijk
SPDX-FileCopyrightText: 2020 Dominik Zajac
SPDX-FileCopyrightText: 2020 Mickaël Cornière
SPDX-FileCopyrightText: 2022 François Darveau
SPDX-FileCopyrightText: 2022 Julian Foad
SPDX-FileCopyrightText: 2022 Warren Bailey
SPDX-FileCopyrightText: 2023 Antonis Christofides
SPDX-FileCopyrightText: 2023 Felix Stupp
SPDX-FileCopyrightText: 2023 Pierre 'McFly' Marty
SPDX-FileCopyrightText: 2024 - 2025 Suguru Hirahara

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# Setting up Miniflux

This is an [Ansible](https://www.ansible.com/) role which installs [Miniflux](https://miniflux.app/) to run as a [Docker](https://www.docker.com/) container wrapped in a systemd service.

Miniflux is a minimalist and opinionated feed reader.

See the project's [documentation](https://miniflux.app/docs/index.html) to learn what Miniflux does and why it might be useful to you.

## Prerequisites

To run a Miniflux instance it is necessary to prepare a [Postgres](https://www.postgresql.org) database server.

If you are looking for an Ansible role for it, you can check out [this role (ansible-role-postgres)](https://github.com/mother-of-all-self-hosting/ansible-role-postgres) maintained by the [Mother-of-All-Self-Hosting (MASH)](https://github.com/mother-of-all-self-hosting) team.

## Adjusting the playbook configuration

To enable Miniflux with this role, add the following configuration to your `vars.yml` file.

**Note**: the path should be something like `inventory/host_vars/mash.example.com/vars.yml` if you use the [MASH Ansible playbook](https://github.com/mother-of-all-self-hosting/mash-playbook).

```yaml
########################################################################
#                                                                      #
# miniflux                                                             #
#                                                                      #
########################################################################

miniflux_enabled: true

########################################################################
#                                                                      #
# /miniflux                                                            #
#                                                                      #
########################################################################
```

### Set the hostname

To enable Miniflux you need to set the hostname as well. To do so, add the following configuration to your `vars.yml` file. Make sure to replace `example.com` with your own value.

```yaml
miniflux_hostname: "example.com"
```

After adjusting the hostname, make sure to adjust your DNS records to point the domain to your server.

### Set variables for connecting to a Postgres database server

To have the Miniflux instance connect to your Postgres server, add the following configuration to your `vars.yml` file.

```yaml
miniflux_database_username: YOUR_POSTGRES_SERVER_USERNAME_HERE
miniflux_database_password: YOUR_POSTGRES_SERVER_PASSWORD_HERE
miniflux_database_hostname: YOUR_POSTGRES_SERVER_HOSTNAME_HERE
miniflux_database_port: 5432
miniflux_database_name: YOUR_POSTGRES_SERVER_DATABASE_NAME_HERE
```

Make sure to replace values for variables with yours.

### Add configurations for admin user (optional)

If you wish to create an admin user on startup, you can specify the username and password of it by adding the following configuration to your `vars.yml` file.

```yaml
miniflux_admin_login: ADMIN_USERNAME_HERE
miniflux_admin_password: ADMIN_PASSWORD_HERE
```

### Extending the configuration

There are some additional things you may wish to configure about the component.

Take a look at:

- [`defaults/main.yml`](../defaults/main.yml) for some variables that you can customize via your `vars.yml` file. You can override settings (even those that don't have dedicated playbook variables) using the `miniflux_environment_variables_additional_variables` variable

See the [documentation](https://miniflux.app/docs/configuration.html) for a complete list of Miniflux's config options that you could put in `miniflux_environment_variables_additional_variables`.

## Installing

After configuring the playbook, run the installation command of your playbook as below:

```sh
ansible-playbook -i inventory/hosts setup.yml --tags=setup-all,start
```

If you use the MASH playbook, the shortcut commands with the [`just` program](https://github.com/mother-of-all-self-hosting/mash-playbook/blob/main/docs/just.md) are also available: `just install-all` or `just setup-all`

## Usage

After running the command for installation, the Miniflux instance becomes available at the URL specified with `miniflux_hostname` and `miniflux_path_prefix`. With the configuration above, the service is hosted at `https://example.com/miniflux`.

To get started, open the URL with a web browser to log in. You can create additional users (admin-privileged or not) after logging in with your administrator username (`miniflux_admin_login`) and password (`miniflux_admin_password`).

## Troubleshooting

### Check the service's logs

You can find the logs in [systemd-journald](https://www.freedesktop.org/software/systemd/man/systemd-journald.service.html) by logging in to the server with SSH and running `journalctl -fu miniflux` (or how you/your playbook named the service, e.g. `mash-miniflux`).
