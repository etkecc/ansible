<!--
SPDX-FileCopyrightText: 2020 - 2024 MDAD project contributors
SPDX-FileCopyrightText: 2020 - 2024 Slavi Pantaleev
SPDX-FileCopyrightText: 2020 Aaron Raimist
SPDX-FileCopyrightText: 2020 Chris van Dijk
SPDX-FileCopyrightText: 2020 Dominik Zajac
SPDX-FileCopyrightText: 2020 Mickaël Cornière
SPDX-FileCopyrightText: 2021 Béla Becker
SPDX-FileCopyrightText: 2021 pushytoxin
SPDX-FileCopyrightText: 2022 felixx9
SPDX-FileCopyrightText: 2022 François Darveau
SPDX-FileCopyrightText: 2022 Jim Myhrberg
SPDX-FileCopyrightText: 2022 Julian Foad
SPDX-FileCopyrightText: 2022 Nikita Chernyi
SPDX-FileCopyrightText: 2022 Warren Bailey
SPDX-FileCopyrightText: 2023 Antonis Christofides
SPDX-FileCopyrightText: 2023 Felix Stupp
SPDX-FileCopyrightText: 2023 Pierre 'McFly' Marty
SPDX-FileCopyrightText: 2024 - 2025 Suguru Hirahara

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# Setting up Etherpad

This is an [Ansible](https://www.ansible.com/) role which installs [Etherpad](https://etherpad.org), an open source collaborative text editor, to run as a [Docker](https://www.docker.com/) container wrapped in a systemd service.

See the project's [documentation](https://docs.etherpad.org/) to learn what Etherpad does and why it might be useful to you.

## Prerequisites

To run an Etherpad instance it is necessary to prepare a database supported by [ueberdb2](https://www.npmjs.com/package/ueberdb2). The role supports [MariaDB](https://mariadb.org), [Postgres](https://www.postgresql.org/), [Redis](https://redis.io/), [SQLite](https://www.sqlite.org/), as well as `memory` (an in-memory ephemeral database). By default it is configured to use Postgres.

If you are looking for an Ansible role for MariaDB, Postgres, and Redis, you can check out [ansible-role-postgres](https://github.com/mother-of-all-self-hosting/ansible-role-postgres), [ansible-role-mariadb](https://github.com/mother-of-all-self-hosting/ansible-role-mariadb), and [ansible-role-redis](https://github.com/mother-of-all-self-hosting/ansible-role-redis), all of which are maintained by the [Mother-of-All-Self-Hosting (MASH)](https://github.com/mother-of-all-self-hosting) team. The roles for [KeyDB](https://keydb.dev/) ([ansible-role-keydb](https://github.com/mother-of-all-self-hosting/ansible-role-keydb)) and [Valkey](https://valkey.io/) ([ansible-role-valkey](https://github.com/mother-of-all-self-hosting/ansible-role-valkey)) are available as well.

## Adjusting the playbook configuration

To enable Etherpad with this role, add the following configuration to your `vars.yml` file.

**Note**: the path should be something like `inventory/host_vars/matrix.example.com/vars.yml` if you use the [matrix-docker-ansible-deploy (MDAD)](https://github.com/spantaleev/matrix-docker-ansible-deploy) or [Mother-of-All-Self-Hosting (MASH)](https://github.com/mother-of-all-self-hosting/mash-playbook) Ansible playbook.

```yaml
########################################################################
#                                                                      #
# etherpad                                                             #
#                                                                      #
########################################################################

etherpad_enabled: true

########################################################################
#                                                                      #
# /etherpad                                                            #
#                                                                      #
########################################################################
```

### Set the hostname

>[!NOTE]
> If you use the MDAD Ansible playbook, it installs Etherpad on the `etherpad.` subdomain (`etherpad.example.com`) by default, so this setting is optional.

To serve Etherpad you need to set the hostname as well. To do so, add the following configuration to your `vars.yml` file. Make sure to replace `example.com` with your own value.

```yaml
# Uncomment and adjust this part if you'd like to use a different scheme than the default
# etherpad_scheme: https

etherpad_hostname: "example.com"
```

After adjusting the hostname, make sure to adjust your DNS records to point the Etherpad domain to your server.

### Configure database

>[!NOTE]
> If you use the MDAD Ansible playbook, any additional configurations are not required as they are specified by default. See its [`matrix_servers`](https://github.com/spantaleev/matrix-docker-ansible-deploy/blob/master/group_vars/matrix_servers) for details.

Etherpad supports databases available with [ueberdb2](https://www.npmjs.com/package/ueberdb2), including MariaDB and Postgres. By default the role is configured to use Postgres for its database.

#### MariaDB

To set up MariaDB for the Etherpad instance, add the following configuration to your `vars.yml` file:

```yaml
etherpad_database_type: mysql
etherpad_database_mysql_username: YOUR_DATABASE_USERNAME_HERE
etherpad_database_mysql_password: YOUR_DATABASE_PASSWORD_HERE
```

Make sure to replace `YOUR_DATABASE_USERNAME_HERE` and `YOUR_DATABASE_PASSWORD_HERE` with your own values.

#### Postgres

To use Postgres, add the following configuration to your `vars.yml` file:

```yaml
etherpad_database_username: YOUR_DATABASE_USERNAME_HERE
etherpad_database_password: YOUR_DATABASE_PASSWORD_HERE
```

#### Redis

To use a Redis data-store (or compatible service like Valkey), add the following configuration to your `vars.yml` file:

```yaml
etherpad_database_type: redis
etherpad_redis_hostname: YOUR_REDIS_SERVER_HOSTNAME_HERE
```

Make sure to replace `YOUR_REDIS_SERVER_HOSTNAME_HERE` with the hostname of your Redis (or the compatible) instance.

#### SQLite

To use a SQLite, you need to specify its path by adding the following configuration to your `vars.yml` file:

```yaml
etherpad_database_type: sqlite
```

The database file will be created inside the directory mounted with `{{ etherpad_data_path }}`.

#### In-memory database

It is also possible to use an in-memory ephemeral database by adding the following configuration to your `vars.yml` file:

```yaml
etherpad_database_type: memory
```

#### Other databases

For other databases like [CouchDB](https://couchdb.apache.org/), add custom configurations to `etherpad_configuration_extension_json`. Refer to [the template settings.json file](https://github.com/ether/etherpad-lite/blob/develop/settings.json.template) for details about necessary settings.

### Create admin user (optional)

You can create an admin user account for authentication. The admin user account is used by:

- default HTTP Basic authentication if no plugin handles authentication
- authentication plugins
- authorization plugins

The admin user can access to `/admin` page. Authentication and authorization plugins may define additional properties. Note that `/admin` page will not be available, if the admin user is not created.

To create the admin user, add the following configuration to your `vars.yml` file. Make sure to replace `YOUR_USERNAME_HERE` and `YOUR_PASSWORD_HERE` with your own values.

```yaml
etherpad_admin_username: YOUR_USERNAME_HERE
etherpad_admin_password: YOUR_PASSWORD_HERE
```

### Enable HSTS preloading (optional)

If you want to enable [HSTS (HTTP Strict-Transport-Security) preloading](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security#preloading_strict_transport_security), add the following configuration to your `vars.yml` file:

```yaml
etherpad_hsts_preload_enabled: true
```

### Allow/disallow embedding Etherpad (optional)

It is possible to control whether embedding Etherpad to a frame on another website will be allowed or not.

By default it is allowed, and you can disallow it by adding the following configuration to your `vars.yml` file:

```yaml
etherpad_framing_enabled: false
```

Setting `false` to the variable disallows Etherpad to be embedded on a website with a different origin by specifying `SAMEORIGIN` to the "X-Frame-Options" response header and `frame-ancestors 'self'` to the Content-Security-Policy (CSP) header, respectively.

### Set the name of the instance (optional)

The name of the instance is set to "Etherpad" by default. To change it, add the following configuration to your `vars.yml` file (adapt to your needs):

```yaml
etherpad_configuration_title: YOUR_INSTANCE_NAME_HERE
```

### Set the default text (optional)

You can also edit the default text on a new pad with the variable `etherpad_configuration_defaultpadtext`. To do so, add the following configuration to your `vars.yml` file (adapt to your needs).

>[!NOTE]
> The whole text (all of its belonging lines) under the variable needs to be indented with 2 spaces.

```yaml
etherpad_configuration_defaultpadtext: |
  Welcome to Etherpad!

  This pad text is synchronized as you type, so that everyone viewing this page sees the same text. This allows you to collaborate seamlessly on documents!

  Get involved with Etherpad at https://etherpad.org
```

### Define plugins to install (optional)

You can also define plugins that should be installed with the variable `etherpad_plugins`. Defining plugins also requires self-building the Etherpad Docker image with the `etherpad_container_image_self_build` variable.

Etherpad plugins can also be managed from the admin page (if enabled). You can view a list of the plugins [on this page](https://static.etherpad.org/index.html).

To specify plugins to install, add the following configuration to your `vars.yml` file (adapt to your needs). No plugins are installed by default.

```yaml
etherpad_container_image_self_build: true
etherpad_plugins:
  - YOUR_FIRST_PLUGIN_HERE
  - YOUR_SECOND_PLUGIN_HERE
```

### Extending the configuration

There are some additional things you may wish to configure about the component.

Take a look at:

- [`defaults/main.yml`](../defaults/main.yml) for some variables that you can customize via your `vars.yml` file. You can override settings (even those that don't have dedicated playbook variables) using the `etherpad_configuration_extension_json` variable

Here is an example of configuration extension:

```yaml
etherpad_configuration_extension_json: |
  {
   "loadTest": true,
   "commitRateLimiting": {
     "duration": 1,
     "points": 10
   },
   "padOptions": {
     "noColors": true,
     "showChat": true,
     "showLineNumbers": false,
     "rtl": true,
     "alwaysShowChat": true,
     "lang": "ar"
   }
  }
```

Check [the official docs](https://etherpad.org/doc/latest/) for available settings.

## Installing

After configuring the playbook, run the installation command of your playbook as below:

```sh
ansible-playbook -i inventory/hosts setup.yml --tags=setup-all,start
```

If you use the MDAD / MASH playbook, the shortcut commands with the [`just` program](https://github.com/spantaleev/matrix-docker-ansible-deploy/blob/master/docs/just.md) are also available: `just install-all` or `just setup-all`

## Usage

The Etherpad UI should be available at the specified hostname like `https://example.com`, while the admin UI (if enabled) should then be available at `https://example.com/admin`.

Check [the official docs](https://etherpad.org/doc/latest/) and [the wiki at GitHub](https://github.com/ether/etherpad-lite/wiki) for details about how to configure and use Etherpad.

### Install plugins

If you have created an admin user, it is possible to install plugins at the admin interface available at `https://example.com/admin/plugins` after logging in to the admin user account.

The list of the plugins hosted on npm is available at the [Plugins website](https://static.etherpad.org).

### Use a hashed admin password

The upstream project [advises](https://github.com/ether/etherpad-lite/blob/develop/README.md#secure-your-installation) to store hashed passwords instead of ones in plain text on your configuration file if you have enabled authentication. This is strongly recommended if you are running a production installation.

To do so, you can install [ep_hash_auth plugin](https://www.npmjs.com/package/ep_hash_auth) on the admin interface, generate the hash of your password locally, and replace `etherpad_admin_password` with `etherpad_admin_hash` as below:

```yaml
etherpad_admin_username: YOUR_USERNAME_HERE
etherpad_admin_hash: YOUR_HASHED_PASSWORD_HERE
```

After replacing the variable, you'll need to re-run the installation command.

### Managing / Deleting old pads

If you want to manage and remove old unused pads from Etherpad, you will first need to create the Etherpad admin user as described above.

After logging in to the admin web UI, go to the plugin manager page, and install the `adminpads2` plugin.

Once the plugin is installed, you should have a "Manage pads" section in the UI.

### Change admin user's password

Even if you change the Etherpad admin user's password (`etherpad_admin_password` in your `vars.yml` file) subsequently, the admin user's credentials on the homeserver won't be updated automatically.

If you'd like to change the admin user's password, use a tool to change it before updating `etherpad_admin_password` to let the admin user know its new password. For MDAD project, you can use [synapse-admin](https://github.com/spantaleev/matrix-docker-ansible-deploy/blob/master/docs/configuring-playbook-synapse-admin.md) to change the password.

## Troubleshooting

You can find the logs in [systemd-journald](https://www.freedesktop.org/software/systemd/man/systemd-journald.service.html) by logging in to the server with SSH and running `journalctl -fu etherpad` (or how you/your playbook named the service, e.g. `matrix-etherpad`).

### Increase logging verbosity

The default logging level for this component is `WARN`. If you want to increase the verbosity, add the following configuration to your `vars.yml` file and re-run the playbook:

```yaml
# Valid values: DEBUG, INFO, WARN, ERROR
etherpad_configuration_loglevel: DEBUG
```
