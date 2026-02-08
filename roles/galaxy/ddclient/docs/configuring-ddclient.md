<!--
SPDX-FileCopyrightText: 2020 Aaron Raimist
SPDX-FileCopyrightText: 2020 Chris van Dijk
SPDX-FileCopyrightText: 2020 Dominik Zajac
SPDX-FileCopyrightText: 2020 Mickaël Cornière
SPDX-FileCopyrightText: 2020 Scott Crossen
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

# Setting up ddclient

This is an [Ansible](https://www.ansible.com/) role which installs [ddclient⁠](https://github.com/ddclient/ddclient) to run as a [Docker](https://www.docker.com/) container wrapped in a systemd service.

ddclient is a Perl client to update dynamic DNS entries for accounts on a wide range of dynamic DNS services.

See the project's [documentation](https://ddclient.net/) to learn what ddclient does and why it might be useful to you.

## Adjusting the playbook configuration

To enable ddclient with this role, add the following configuration to your `vars.yml` file.

**Note**: the path should be something like `inventory/host_vars/mash.example.com/vars.yml` if you use the [MASH Ansible playbook](https://github.com/mother-of-all-self-hosting/mash-playbook).

```yaml
########################################################################
#                                                                      #
# ddclient                                                             #
#                                                                      #
########################################################################

ddclient_enabled: true

########################################################################
#                                                                      #
# /ddclient                                                            #
#                                                                      #
########################################################################
```

### Add configurations for dynamic DNS provider

To enable the service it is also required to add configurations for your dynamic DNS provider. You need to specify at least `domain` and `protocol` keys.

```yaml
ddclient_domain_configurations:
  - provider: DYNAMIC_DNS_PROVIDER_HERE
    protocol: DYNAMIC_DNS_PROVIDER_PROTOCOL_HERE
    username: YOUR_USERNAME_HERE
    password: YOUR_PASSWORD_HERE
    domain: YOUR_DOMAIN_HERE
```

Keep in mind that certain providers may require a different configuration for the `ddclient_domain_configurations` variable. In most cases this is simply a username and password but can differ from provider to provider. Please consult with [this configuration example](https://github.com/ddclient/ddclient/blob/main/ddclient.conf.in) and your provider's documentation to determine what you'll need to provide to authenticate with your DNS provider.

### Setting the endpoint to obtain IP address (optional)

As the default router is set to `web`, its default endpoint to obtain IP address is set to `dyndns`. You can specify another endpoint by adding the following configuration to your `vars.yml` file:

```yaml
# Example: https://cloudflare.com/cdn-cgi/trace
ddclient_web: ENDPOINT_TO_OBTAIN_IP_ADDRESS_HERE
```

It is also possible to specify the field to extract the IP address from. Leave it empty if your endpoint defined in `ddclient_web` does not need it.

```yaml
# Example: ip=
ddclient_web_skip: FIELD_TO_EXTRACT_IP_ADDRESS_HERE
```

### Configuring router option (optional)

By default the service is configured to use `web` as the option for a router, from which ddclient is to retrieve an IP address. See [this page](https://ddclient.net/routers.html) on the official documentation for details.

To change the router to `if`, you can add the following configuration to your `vars.yml` file:

```yaml
ddclient_use: if
```

### Extending the configuration

There are some additional things you may wish to configure about the service.

Take a look at:

- [`defaults/main.yml`](../defaults/main.yml) for some variables that you can customize via your `vars.yml` file. You can override settings (even those that don't have dedicated playbook variables) using `ddclient_additional_configuration_blocks` and `ddclient_environment_variables_additional_variables` variables

## Installing

After configuring the playbook, run the installation command of your playbook as below:

```sh
ansible-playbook -i inventory/hosts setup.yml --tags=setup-all,start
```

If you use the MASH playbook, the shortcut commands with the [`just` program](https://github.com/mother-of-all-self-hosting/mash-playbook/blob/main/docs/just.md) are also available: `just install-all` or `just setup-all`

## Usage

After running the command for installation, ddclient becomes available. Your DNS entry will be automatically updated per seconds specified to `ddclient_daemon_interval` (300 seconds by default).

## Troubleshooting

The FAQ page is available at <https://ddclient.net/FAQ.html>.

### Check the service's logs

You can find the logs in [systemd-journald](https://www.freedesktop.org/software/systemd/man/systemd-journald.service.html) by logging in to the server with SSH and running `journalctl -fu ddclient` (or how you/your playbook named the service, e.g. `mash-ddclient`).

Due to an [upstream issue](https://github.com/linuxserver/docker-ddclient/issues/54#issuecomment-1153143132) the logging output is not always complete. For advanced debugging purposes running the `ddclient` tool outside of the container is useful via the following: `ddclient -file ./ddclient.conf -daemon=0 -debug -verbose -noquiet`.
