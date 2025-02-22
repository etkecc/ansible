<!--
SPDX-FileCopyrightText: 2021 Béla Becker
SPDX-FileCopyrightText: 2021 - 2024 Slavi Pantaleev
SPDX-FileCopyrightText: 2021 pushytoxin
SPDX-FileCopyrightText: 2022 Jim Myhrberg
SPDX-FileCopyrightText: 2022 Nikita Chernyi
SPDX-FileCopyrightText: 2022 felixx9
SPDX-FileCopyrightText: 2024 - 2025 Suguru Hirahara

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# Setting up Etherpad

This is an [Ansible](https://www.ansible.com/) role which installs [Etherpad](https://etherpad.org), an open source collaborative text editor, to run as a [Docker](https://www.docker.com/) container wrapped in a systemd service.

## Adjusting the playbook configuration

To enable Etherpad with this role, add the following configuration to your `vars.yml` file.

**Note**: the path should be something like `inventory/host_vars/matrix.example.com/vars.yml` if you use the [MDAD (matrix-docker-ansible-deploy)](https://github.com/spantaleev/matrix-docker-ansible-deploy) Ansible playbook.

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

**Note**: if you use the MDAD Ansible playbook, it installs Etherpad on the `etherpad.` subdomain (`etherpad.example.com`) by default, so this setting is optional.

To serve Etherpad you need to set the hostname as well. To do so, add the following configuration to your `vars.yml` file. Make sure to replace `example.com` with your own value.

```yaml
# Uncomment and adjust this part if you'd like to use a different scheme than the default
# etherpad_scheme: https

etherpad_hostname: "example.com"
```

After adjusting the hostname, make sure to adjust your DNS records to point the Etherpad domain to your server.

### Set the username and password of database

**Note**: if you use the MDAD Ansible playbook, these settings are not needed as they are specified by default. See its [`matrix_servers`](https://github.com/spantaleev/matrix-docker-ansible-deploy/blob/master/group_vars/matrix_servers) for details.

Add the following configuration to your `vars.yml` file for the database, which Etherpad is going to use.

Make sure to replace `YOUR_DATABASE_USERNAME_HERE` and `YOUR_DATABASE_PASSWORD_HERE` with your own values. **Do not use the default password**, which is set to `some-password` on the `main.yml` file.

```yaml
etherpad_database_username: YOUR_DATABASE_USERNAME_HERE
etherpad_database_password: YOUR_DATABASE_PASSWORD_HERE
```

### Create admin user (optional)

You can create an admin user account for authentication. The admin user account is used by:
  - default HTTP basic authentication if no plugin handles authentication
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
etherpad_title: YOUR_INSTANCE_NAME_HERE
```

### Set the default text (optional)

You can also edit the default text on a new pad with the variable `etherpad_default_pad_text`. To do so, add the following configuration to your `vars.yml` file (adapt to your needs).

**Note**: the whole text (all of its belonging lines) under the variable needs to be indented with 2 spaces.

```yaml
etherpad_default_pad_text: |
  Welcome to Etherpad!

  This pad text is synchronized as you type, so that everyone viewing this page sees the same text. This allows you to collaborate seamlessly on documents!

  Get involved with Etherpad at https://etherpad.org
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

If you use the [mash-playbook](https://github.com/mother-of-all-self-hosting/mash-playbook) or MDAD Ansible playbook, the shortcut commands with the [`just` program](https://github.com/spantaleev/matrix-docker-ansible-deploy/blob/master/docs/just.md) are also available: `just install-all` or `just setup-all`

## Usage

The Etherpad UI should be available at the specified hostname like `https://example.com`, while the admin UI (if enabled) should then be available at `https://example.com/admin`.

Check [the official docs](https://etherpad.org/doc/latest/) and [the wiki at GitHub](https://github.com/ether/etherpad-lite/wiki) for details about how to configure and use Etherpad.

### Install plugins

If you have created an admin user, it is possible to install plugins at the admin interface available at https://example.com/admin/plugins after logging in to the admin user account.

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

As with all other services, you can find the logs in [systemd-journald](https://www.freedesktop.org/software/systemd/man/systemd-journald.service.html) by logging in to the server with SSH and running `journalctl -fu etherpad` (or how you/your playbook named the service, e.g. `matrix-etherpad`).

### Increase logging verbosity

The default logging level for this component is `WARN`. If you want to increase the verbosity, add the following configuration to your `vars.yml` file and re-run the playbook:

```yaml
# Valid values: ERROR, WARN, INFO, DEBUG
etherpad_configuration_extension_json: |
 {
  "loglevel": "DEBUG",
 }
```
