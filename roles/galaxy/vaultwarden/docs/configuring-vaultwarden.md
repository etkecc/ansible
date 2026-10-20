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
SPDX-FileCopyrightText: 2023 Alejandro AR
SPDX-FileCopyrightText: 2023 Antonis Christofides
SPDX-FileCopyrightText: 2023 Felix Stupp
SPDX-FileCopyrightText: 2023 Julian-Samuel Gebühr
SPDX-FileCopyrightText: 2023 Pierre 'McFly' Marty
SPDX-FileCopyrightText: 2024 Thomas Miceli
SPDX-FileCopyrightText: 2024-2026 Suguru Hirahara

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# Setting up Vaultwarden

This is an [Ansible](https://www.ansible.com/) role which installs [Vaultwarden](https://github.com/dani-garcia/vaultwarden) to run as a [Docker](https://www.docker.com/) container wrapped in a systemd service.

Vaultwarden is an unofficial [Bitwarden](https://bitwarden.com/) compatible server.

See the project's [documentation](https://github.com/dani-garcia/vaultwarden/blob/main/README.md) to learn what Vaultwarden does and why it might be useful to you.

## Prerequisites

To run a Vaultwarden instance it is necessary to prepare a database. You can use a [MySQL](https://www.mysql.com/) compatible database server, [Postgres](https://www.postgresql.org/), or [SQLite](https://www.sqlite.org/). The SQLite database file will be automatically created by the service if it is enabled.

If you are looking for Ansible roles for a MySQL compatible server or Postgres, you can check out [ansible-role-mariadb](https://github.com/mother-of-all-self-hosting/ansible-role-mariadb) and [ansible-role-postgres](https://github.com/mother-of-all-self-hosting/ansible-role-postgres), both of which are maintained by the [Mother-of-All-Self-Hosting (MASH)](https://github.com/mother-of-all-self-hosting) team.

## Adjusting the playbook configuration

To enable Vaultwarden with this role, add the following configuration to your `vars.yml` file.

**Note**: the path should be something like `inventory/host_vars/mash.example.com/vars.yml` if you use the [MASH Ansible playbook](https://github.com/mother-of-all-self-hosting/mash-playbook).

```yaml
########################################################################
#                                                                      #
# vaultwarden                                                          #
#                                                                      #
########################################################################

vaultwarden_enabled: true

########################################################################
#                                                                      #
# /vaultwarden                                                         #
#                                                                      #
########################################################################
```

### Set the hostname

To enable Vaultwarden you need to set the hostname as well. To do so, add the following configuration to your `vars.yml` file. Make sure to replace `example.com` with your own value.

```yaml
vaultwarden_hostname: "example.com"
```

After adjusting the hostname, make sure to adjust your DNS records to point the domain to your server.

>[!NOTE]
> For additional security, it is recommended to host the Vaultwarden instance at a subpath with `vaultwarden_path_prefix`. When using the path prefix, Vaultwarden will be available at `https://example.com/PATH_PREFIX`, while opening the home page URL (/) returns a 404 HTTP error. Refer to [this page](https://github.com/dani-garcia/vaultwarden/wiki/Hardening-Guide#hiding-under-a-subdir) on the official documentation for details.

### Setting a random string for admin secret (optional)

You also need to set a random string used as administration secret to access the `/admin` section. To do so, add the following configuration to your `vars.yml` file. The value can be generated with `pwgen -s 64 1` or in another way.

```yaml
vaultwarden_config_admin_token: YOUR_SECRET_KEY_HERE
```

Removing the line will disable the `/admin` section.

### Configuring database

#### Specify database (optional)

You can specify a database used by Vaultwarden. By default it is configured to use Postgres.

To use SQLite, add the following configuration to your `vars.yml` file:

```yaml
vaultwarden_database_type: sqlite
```

Set `mysql` to use a MySQL compatible database. The SQLite database is stored in the directory specified with `vaultwarden_data_path`.

For other settings, check variables such as `vaultwarden_database_*` on [`defaults/main.yml`](../defaults/main.yml).

#### Configuring connection to the database server (optional)

By default the role is configured to establish the connection to the database server via a Unix socket. You can mount the Unix socket by adding the following configuration to your `vars.yml` file:

```yaml
# Specify the path to the MySQL compatible server's Unix socket path on the host (bind-mount source)
vaultwarden_database_mysql_socket_path_host: ""

# Specify the path to the Postgres Unix socket path on the host (bind-mount source)
vaultwarden_database_postgres_socket_path_host: ""
```

Setting it enables to connect to the database server via Unix socket mounted in the container.

If TCP connection is preferred, connection via the Unix socket can be disabled by adding the following configuration to your `vars.yml` file:

```yaml
# Disable the connection to the MySQL compatible server via a Unix socket
vaultwarden_database_mysql_socket_enabled: false

# Disable the connection to the Postgres server via a Unix socket
vaultwarden_database_postgres_socket_enabled: false
```

### Enabling user registration (optional)

By default the role is configured to disable user registration. You can enable it by adding the following configuration to your `vars.yml` file:

```yaml
vaultwarden_config_signups_enabled: true
```

### Enabling user verification (optional)

To require email address verification before users can log in to the Vaultwarden instance, add the following configuration to your `vars.yml` file:

```yaml
vaultwarden_config_signups_verify: true
```

>[!NOTE]
> When enabled, settings for a SMTP mailer are required to be specified.

### Configuring the mailer (optional)

To configure a SMTP mailer, add the following configuration to your `vars.yml` file as below (adapt to your needs):

```yaml
# Specify SMTP server hostname
vaultwarden_environment_variables_smtp_host: ""

# Specify SMTP server port number
vaultwarden_environment_variables_smtp_port: 587

# Specify SMTP server username
vaultwarden_environment_variables_smtp_username: ""

# Specify SMTP server password
vaultwarden_environment_variables_smtp_password: ""

# Specify the email address that emails will be sent from
vaultwarden_environment_variables_smtp_from: ""

# Specify the SMTP Auth Type
vaultwarden_environment_variables_smtp_security: starttls
```

>[!WARNING]
> Without setting an authentication method such as DKIM, SPF, and DMARC for your hostname, emails are most likely to be quarantined as spam at recipient's mail servers. The worst scenario is that your server's IP address or hostname will be included in the spam list such as the one managed by [Spamhaus](https://www.spamhaus.org/). If you have set up a mail server with the [MASH project's exim-relay Ansible role](https://github.com/mother-of-all-self-hosting/ansible-role-exim-relay), you can enable DKIM signing with it. Refer [its documentation](https://github.com/mother-of-all-self-hosting/ansible-role-exim-relay/blob/main/docs/configuring-exim-relay.md#enable-dkim-support-optional) for details.

### Extending the configuration

There are some additional things you may wish to configure about the service.

Take a look at:

- [`defaults/main.yml`](../defaults/main.yml) for some variables that you can customize via your `vars.yml` file. You can override settings (even those that don't have dedicated playbook variables) using the `vaultwarden_environment_variables_additional_variables` variable

Refer to [the official documentation](https://github.com/dani-garcia/vaultwarden/blob/main/.env.template) for a complete list of Vaultwarden's config options that you can put in `vaultwarden_environment_variables_additional_variables`.

## Installing

After configuring the playbook, run the installation command of your playbook as below:

```sh
ansible-playbook -i inventory/hosts setup.yml --tags=setup-all,start
```

If you use the MASH playbook, the shortcut commands with the [`just` program](https://github.com/mother-of-all-self-hosting/mash-playbook/blob/main/docs/just.md) are also available: `just install-all` or `just setup-all`

## Usage

After running the command for installation, Vaultwarden becomes available at the specified hostname like `https://example.com`.

To get started, open the URL `https://example.com/PATH_PREFIX/admin` with a web browser to create an account. Note the URL is accessible with an admin token, as specified with `vaultwarden_config_admin_token` on your `vars.yml` file.

If you hadn't enabled the `/admin` feature (by defining `vaultwarden_config_admin_token`), you would:

- **either** need to do so and re-run the playbook
- **or** to enable public registration (`vaultwarden_config_signups_enabled: true`) at least temporarily.

## Troubleshooting

### Check the service's logs

You can find the logs in [systemd-journald](https://www.freedesktop.org/software/systemd/man/systemd-journald.service.html) by logging in to the server with SSH and running `journalctl -fu vaultwarden` (or how you/your playbook named the service, e.g. `mash-vaultwarden`).

#### Increase logging verbosity

If you want to increase the verbosity, add the following configuration to your `vars.yml` file:

```yaml
vaultwarden_config_log_level: debug
```
