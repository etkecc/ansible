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
SPDX-FileCopyrightText: 2023 - 2025 MASH project contributors
SPDX-FileCopyrightText: 2023 Antonis Christofides
SPDX-FileCopyrightText: 2023 Felix Stupp
SPDX-FileCopyrightText: 2023 Pierre 'McFly' Marty
SPDX-FileCopyrightText: 2024 - 2025 Suguru Hirahara

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# Setting up linkding

This is an [Ansible](https://www.ansible.com/) role which installs [linkding](https://linkding.link) to run as a [Docker](https://www.docker.com/) container wrapped in a systemd service.

linkding is a bookmark manager that is designed be to be minimal and fast.

See the project's [documentation](https://linkding.link/installation/) to learn what linkding does and why it might be useful to you.

## Prerequisites

To run a linkding instance it is necessary to prepare a database. You can use a [Postgres](https://www.postgresql.org/) database server or [SQLite](https://www.sqlite.org/). By default it is configured to use SQLite.

If you are looking for an Ansible role for Postgres, you can check out [this role (ansible-role-postgres)](https://github.com/mother-of-all-self-hosting/ansible-role-postgres) maintained by the [Mother-of-All-Self-Hosting (MASH)](https://github.com/mother-of-all-self-hosting) team.

## Adjusting the playbook configuration

To enable linkding with this role, add the following configuration to your `vars.yml` file.

**Note**: the path should be something like `inventory/host_vars/mash.example.com/vars.yml` if you use the [MASH Ansible playbook](https://github.com/mother-of-all-self-hosting/mash-playbook).

```yaml
########################################################################
#                                                                      #
# linkding                                                             #
#                                                                      #
########################################################################

linkding_enabled: true

########################################################################
#                                                                      #
# /linkding                                                            #
#                                                                      #
########################################################################
```

### Set the hostname

To enable linkding you need to set the hostname as well. To do so, add the following configuration to your `vars.yml` file. Make sure to replace `example.com` with your own value.

```yaml
linkding_hostname: "example.com"
```

After adjusting the hostname, make sure to adjust your DNS records to point the domain to your server.

### Set variables for connecting to a Postgres database server

To have the linkding instance connect to your Postgres server, add the following configuration to your `vars.yml` file.

```yaml
linkding_database_type: postgres
linkding_database_hostname: YOUR_POSTGRES_SERVER_HOSTNAME_HERE
linkding_database_port: 5432
linkding_database_username: YOUR_POSTGRES_SERVER_USERNAME_HERE
linkding_database_password: YOUR_POSTGRES_SERVER_PASSWORD_HERE
linkding_database_name: YOUR_POSTGRES_SERVER_DATABASE_NAME_HERE
```

Make sure to replace values for variables with yours.

### Configure superuser (optional)

You can optionally create an initial "superuser" by adding the following configuration to your `vars.yml` file:

```yaml
linkding_superuser_username: SUPERUSER_USERNAME_HERE
linkding_superuser_password: SUPERUSER_PASSWORD_HERE
```

### Extending the configuration

There are some additional things you may wish to configure about the service.

Take a look at:

- [`defaults/main.yml`](../defaults/main.yml) for some variables that you can customize via your `vars.yml` file. You can override settings (even those that don't have dedicated playbook variables) using the `linkding_environment_variables_additional_variables` variable

See the [documentation](https://linkding.link/options/) for a complete list of linkding's config options that you could put in `linkding_environment_variables_additional_variables`.

## Installing

After configuring the playbook, run the installation command of your playbook as below:

```sh
ansible-playbook -i inventory/hosts setup.yml --tags=setup-all,start
```

If you use the MASH playbook, the shortcut commands with the [`just` program](https://github.com/mother-of-all-self-hosting/mash-playbook/blob/main/docs/just.md) are also available: `just install-all` or `just setup-all`

## Usage

After running the command for installation, the linkding instance becomes available at the URL specified with `linkding_hostname`. With the configuration above, the service is hosted at `https://example.com`.

To get started, open the URL with a web browser, and log in with the superuser's login credential.

## Troubleshooting

### Check the service's logs

You can find the logs in [systemd-journald](https://www.freedesktop.org/software/systemd/man/systemd-journald.service.html) by logging in to the server with SSH and running `journalctl -fu linkding` (or how you/your playbook named the service, e.g. `mash-linkding`).
