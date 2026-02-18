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
SPDX-FileCopyrightText: 2024-2026 Suguru Hirahara

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# Setting up Hydrogen

This is an [Ansible](https://www.ansible.com/) role which installs [Hydrogen](https://github.com/element-hq/hydrogen-web) to run as a [Docker](https://www.docker.com/) container wrapped in a systemd service.

Hydrogen is a lightweight web client for [Matrix](https://matrix.org/), realtime communication (chat) network, with legacy and mobile browser support.

See the project's [documentation](https://github.com/element-hq/hydrogen-web/blob/master/README.md) to learn what Hydrogen does and why it might be useful to you.

>[!NOTE]
> This role merely enables you to set up the client; To communicate with other people on the Matrix network you need to prepare a Matrix homeserver which this client can connect to. While it is still possible to use a public homeserver with the Hydrogen instance, [this "matrix-docker-ansible-deploy" Ansible playbook](https://github.com/spantaleev/matrix-docker-ansible-deploy/) lets you set up Matrix services from the core ones such as a homeserver to other goodies like "bridges" on your server — it is pretty complete and well maintained.

## Adjusting the playbook configuration

To enable Hydrogen with this role, add the following configuration to your `vars.yml` file.

**Note**: the path should be something like `inventory/host_vars/matrix.example.com/vars.yml` if you use the [MDAD Ansible playbook](https://github.com/spantaleev/matrix-docker-ansible-deploy).

```yaml
########################################################################
#                                                                      #
# hydrogen                                                             #
#                                                                      #
########################################################################

hydrogen_enabled: true

########################################################################
#                                                                      #
# /hydrogen                                                            #
#                                                                      #
########################################################################
```

### Set the hostname

To enable Hydrogen you need to set the hostname as well. To do so, add the following configuration to your `vars.yml` file. Make sure to replace `example.com` with your own value.

```yaml
hydrogen_hostname: "example.com"
```

After adjusting the hostname, make sure to adjust your DNS records to point the domain to your server.

### Set the default homeserver URL

It is also necessary to specify the default homeserver's URL by adding the following configuration to your `vars.yml` file:

```yaml
hydrogen_default_hs_url: YOUR_HOMESERVER_URL_HERE
```

### Extending the configuration

There are some additional things you may wish to configure about the service.

Take a look at:

- [`defaults/main.yml`](../defaults/main.yml) for some variables that you can customize via your `vars.yml` file
- [`templates/config.json.j2`](../templates/config.json.j2) for the component's default configuration. You can override settings (even those that don't have dedicated playbook variables) using the `hydrogen_configuration_extension_json` variable

## Installing

After configuring the playbook, run the installation command of your playbook as below:

```sh
ansible-playbook -i inventory/hosts setup.yml --tags=setup-all,start
```

If you use the MDAD playbook, the shortcut commands with the [`just` program](https://github.com/spantaleev/matrix-docker-ansible-deploy/blob/master/docs/just.md) are also available: `just install-all` or `just setup-all`

## Usage

After running the command for installation, Hydrogen becomes available at the specified hostname like `https://example.com`.

To get started, open the URL with a web browser, and log in to your homeserver with the Matrix account.

## Troubleshooting

### Check the service's logs

You can find the logs in [systemd-journald](https://www.freedesktop.org/software/systemd/man/systemd-journald.service.html) by logging in to the server with SSH and running `journalctl -fu hydrogen` (or how you/your playbook named the service, e.g. `matrix-client-hydrogen`).
