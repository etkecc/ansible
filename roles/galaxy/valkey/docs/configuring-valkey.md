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

# Setting up Valkey

This is an [Ansible](https://www.ansible.com/) role which installs [Valkey](https://valkey.io/) to run as a [Docker](https://www.docker.com/) container wrapped in a systemd service.

Valkey is a fork of [Redis](https://redis.io/), a flexible distributed key-value datastore that is optimized for caching and other realtime workloads.

See the project's [documentation](https://valkey.io/docs/) to learn what Valkey does and why it might be useful to you.

> [!WARNING]
> Because Valkey is not as flexible as Postgres when it comes to authentication and data separation, it's **recommended that you run separate Valkey instances** (one for each service). Valkey supports multiple database and a [SELECT](https://valkey.io/commands/select/) command for switching between them. However, **reusing the same Valkey instance is not good enough** because:
>
> - if all services use the same Valkey instance and database (id = 0), services may conflict with one another
> - the number of databases is limited to [16 by default](https://github.com/valkey-io/valkey/blob/33f42d7fb597ce28040f184ee57ed86d6f6ffbd8/valkey.conf#L396), which may or may not be enough. With configuration changes, this is solvable.
> - some services do not support switching the Valkey database and always insist on using the default one (id = 0)
> - Valkey [does not support different authentication credentials for its different databases](https://stackoverflow.com/a/37262596), so each service can potentially read and modify other services' data

## Adjusting the playbook configuration

To enable Valkey with this role, add the following configuration to your `vars.yml` file.

**Note**: the path should be something like `inventory/host_vars/mash.example.com/vars.yml` if you use the [MASH Ansible playbook](https://github.com/mother-of-all-self-hosting/mash-playbook).

```yaml
########################################################################
#                                                                      #
# valkey                                                               #
#                                                                      #
########################################################################

valkey_enabled: true

########################################################################
#                                                                      #
# /valkey                                                              #
#                                                                      #
########################################################################
```

### Extending the configuration

There are some additional things you may wish to configure about the service.

Take a look at:

- [`defaults/main.yml`](../defaults/main.yml) for some variables that you can customize via your `vars.yml` file. You can override settings (even those that don't have dedicated playbook variables) using the `valkey_environment_variables_additional_variables` variable

## Installing

After configuring the playbook, run the installation command of your playbook as below:

```sh
ansible-playbook -i inventory/hosts setup.yml --tags=setup-all,start
```

If you use the MASH playbook, the shortcut commands with the [`just` program](https://github.com/mother-of-all-self-hosting/mash-playbook/blob/main/docs/just.md) are also available: `just install-all` or `just setup-all`

## Usage

After running the command for installation, Valkey becomes available.

## Troubleshooting

### Check the service's logs

You can find the logs in [systemd-journald](https://www.freedesktop.org/software/systemd/man/systemd-journald.service.html) by logging in to the server with SSH and running `journalctl -fu valkey` (or how you/your playbook named the service, e.g. `mash-valkey`).
