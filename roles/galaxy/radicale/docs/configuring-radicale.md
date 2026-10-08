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
SPDX-FileCopyrightText: 2023 Pierre 'McFly' Marty
SPDX-FileCopyrightText: 2024-2026 Suguru Hirahara

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# Setting up Radicale

This is an [Ansible](https://www.ansible.com/) role which installs [Radicale](https://radicale.org/) to run as a [Docker](https://www.docker.com/) container wrapped in a systemd service.

Radicale is a free and open-source CalDAV and CardDAV server (solution for hosting contacts and calendars).

See the project's [documentation](https://radicale.org/v3.html#documentation-1) to learn what Radicale does and why it might be useful to you.

## Adjusting the playbook configuration

To enable Radicale with this role, add the following configuration to your `vars.yml` file.

**Note**: the path should be something like `inventory/host_vars/mash.example.com/vars.yml` if you use the [MASH Ansible playbook](https://github.com/mother-of-all-self-hosting/mash-playbook).

```yaml
########################################################################
#                                                                      #
# radicale                                                             #
#                                                                      #
########################################################################

radicale_enabled: true

########################################################################
#                                                                      #
# /radicale                                                            #
#                                                                      #
########################################################################
```

### Set the hostname

To enable Radicale you need to set the hostname as well. To do so, add the following configuration to your `vars.yml` file. Make sure to replace `example.com` with your own value.

```yaml
radicale_hostname: "example.com"
```

After adjusting the hostname, make sure to adjust your DNS records to point the domain to your server.

### Configuring HTTP Basic authentication

This role is configured to enable the HTTP Basic authentication by default.

You can use `htpasswd` to generate the user and password pair, which needs to be set to `radicale_htpasswds` as below:

```yaml
radicale_htpasswds:
  - 'someone:$apr1$Dz1QzvR9$TQj8rP2QfLz7dYkP6Y0K4/'
  - 'another:$apr1$QfJ1mU7a$gR0d9D0dKfIDm0w3lN4hY0'
```

>[!NOTE]
> The legacy `radicale_credentials` convenience variable is discouraged, because it depends on the `passlib` Python library, may be affected by passlib/bcrypt compatibility issues (see: <https://foss.heptapod.net/python-libs/passlib/-/issues/196>), and produces non-deterministic hashes which can trigger unnecessary Ansible changes.

### Extending the configuration

There are some additional things you may wish to configure about the service.

Take a look at:

- [`defaults/main.yml`](../defaults/main.yml) for some variables that you can customize via your `vars.yml` file. You can override settings (even those that don't have dedicated playbook variables) using the `radicale_environment_variables_additional_variables` variable

## Installing

After configuring the playbook, run the installation command of your playbook as below:

```sh
ansible-playbook -i inventory/hosts setup.yml --tags=setup-all,start
```

If you use the MASH playbook, the shortcut commands with the [`just` program](https://github.com/mother-of-all-self-hosting/mash-playbook/blob/main/docs/just.md) are also available: `just install-all` or `just setup-all`

## Usage

After running the command for installation, Radicale becomes available at the specified hostname like `https://example.com`.

To use it, open the URL on the browser to log in to the instance with the credentials.

### Creating new users

Creating new users requires changing the `radicale_htpasswds` variable and re-running the installation command.

## Troubleshooting

### Check the service's logs

You can find the logs in [systemd-journald](https://www.freedesktop.org/software/systemd/man/systemd-journald.service.html) by logging in to the server with SSH and running `journalctl -fu radicale` (or how you/your playbook named the service, e.g. `mash-radicale`).
