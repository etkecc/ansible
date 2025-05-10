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
SPDX-FileCopyrightText: 2023 Julian-Samuel Gebühr
SPDX-FileCopyrightText: 2023 Pierre 'McFly' Marty
SPDX-FileCopyrightText: 2024 - 2025 Suguru Hirahara

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# Setting up Uptime Kuma

This is an [Ansible](https://www.ansible.com/) role which installs [Uptime Kuma](https://github.com/louislam/uptime-kuma) to run as a [Docker](https://www.docker.com/) container wrapped in a systemd service.

Uptime Kuma is a fancy self-hosted monitoring tool similar to [Uptime Robot](https://uptimerobot.com/). It has functions such as below:

- Monitoring uptime for HTTP(s) / TCP / HTTP(s) Keyword / HTTP(s) Json Query / Ping / DNS Record / Push / Steam Game Server / Docker Containers
- Fancy, Reactive, Fast UI/UX
- Notifications via Matrix, Telegram, Discord, Gotify, Slack, Pushover, Email (SMTP), and [90+ notification services](https://github.com/louislam/uptime-kuma/tree/master/src/components/notifications)
- 20-second intervals
- [Multi-Language](https://github.com/louislam/uptime-kuma/tree/master/src/lang)
- Multiple status pages
- Map status pages to specific domains
- Ping chart
- Certificate info
- Proxy support
- 2FA support

See the project's [documentation](https://github.com/louislam/uptime-kuma/wiki) to learn what Uptime Kuma does and why it might be useful to you.

✨ Kuma (くま/熊) means bear 🐻 in Japanese.

## Adjusting the playbook configuration

To enable Uptime Kuma with this role, add the following configuration to your `vars.yml` file.

```yaml
########################################################################
#                                                                      #
# uptime-kuma                                                          #
#                                                                      #
########################################################################

uptime_kuma_enabled: true

########################################################################
#                                                                      #
# /uptime-kuma                                                         #
#                                                                      #
########################################################################
```

### Set the hostname

To enable Uptime Kuma you need to set the hostname as well. To do so, add the following configuration to your `vars.yml` file. Make sure to replace `example.com` with your own value.

```yaml
uptime_kuma_hostname: "example.com"
```

After adjusting the hostname, make sure to adjust your DNS records to point the domain to your server.

**Note**: hosting Uptime Kuma under a subpath (by configuring the `uptime_kuma_path_prefix` variable) does not seem to be possible due to Uptime Kuma's technical limitations.

## Installing

After configuring the playbook, run the installation command of your playbook as below:

```sh
ansible-playbook -i inventory/hosts setup.yml --tags=setup-all,start
```

If you use the MASH playbook, the shortcut commands with the [`just` program](https://github.com/mother-of-all-self-hosting/mash-playbook/blob/main/docs/just.md) are also available: `just install-all` or `just setup-all`

## Usage

After running the command for installation, Uptime Kuma becomes available at the specified hostname like `https://example.com`.

To get started, go to the URL on a web browser and create your admin account. You can then add monitors for web services as many as you like.

## Troubleshooting

### Check the service's logs

You can find the logs in [systemd-journald](https://www.freedesktop.org/software/systemd/man/systemd-journald.service.html) by logging in to the server with SSH and running `journalctl -fu uptime-kuma` (or how you/your playbook named the service, e.g. `mash-uptime-kuma`).
