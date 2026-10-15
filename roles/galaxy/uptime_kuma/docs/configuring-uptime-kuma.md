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
# uptime_kuma                                                          #
#                                                                      #
########################################################################

uptime_kuma_enabled: true

########################################################################
#                                                                      #
# /uptime_kuma                                                         #
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

To get started, open the URL on a web browser and create your admin account. You can then add monitors for web services as many as you like.

## Upgrading from Uptime Kuma 1.x to 2.x

Uptime Kuma 2.x migrates its database on the first start after the upgrade. The [upstream migration guide](https://github.com/louislam/uptime-kuma/wiki/Migration-From-v1-To-v2) is explicit about the stakes: the migration is one-way, it can take hours on larger instances, and interrupting it leaves the database unusable, with a restore from backup as the only way out.

The role performs the upgrade as soon as `uptime_kuma_version` points at a 2.x release, so the migration starts on the next playbook run without an extra confirmation step.

Before upgrading:

1. Stop Uptime Kuma (`systemctl stop uptime-kuma`, or however you named the unit, e.g. `mash-uptime-kuma`).
2. Back up the data directory (by default `/uptime-kuma/data`), for example with `tar -czf uptime-kuma-data.tar.gz -C /uptime-kuma data`.
3. Run the playbook.
4. Watch the migration finish with `journalctl -fu uptime-kuma` (or how you named the unit) before anything restarts the service. Uptime Kuma answers with a "Migration is in progress" page while it runs.

### Image flavors

Uptime Kuma 1.x published the `-alpine` flavor this role used by default. 2.x has these instead:

| Tag (`uptime_kuma_container_image_tag`) | Contents |
| ------ | -------- |
| `{{ uptime_kuma_version }}-slim` (the default) | No bundled Chromium and no embedded MariaDB, the same feature set as the retired `-alpine` flavor |
| `{{ uptime_kuma_version }}` | Bundled Chromium (for Browser Engine monitor types) and an embedded MariaDB |
| `{{ uptime_kuma_version }}-rootless` (and its `-slim-rootless` variant) | The same images with `USER node` baked in, which this role overrides with its own `--user`, so the flavor changes nothing here. Upstream advises against these flavors for 1.x to 2.x upgrades, and the Docker monitor type needs root by default |

If your configuration overrides `uptime_kuma_container_image_tag`, make sure it names a 2.x tag before upgrading: a `-alpine` tag no longer exists and the image pull fails.

### Database configuration

2.x asks for a database backend on first start. The role seeds a `db-config.json` with SQLite into the data directory, which is the backend 1.x installations have always used, so a fresh instance starts straight into the setup wizard instead of that question. Upgrading from 1.x works the same way, because 2.x finds the existing `kuma.db` and treats it as SQLite on its own.

To use MariaDB or the embedded MariaDB of the full image instead, delete the file and answer the database-selection page, or configure `UPTIME_KUMA_DB_*` variables through `uptime_kuma_environment_variables_additional_variables`.

### Ping monitors

The role grants the container the `NET_RAW` capability that ping monitors need in 2.x: the Debian based image ships `/usr/bin/ping` with a `cap_net_raw` file capability, and that binary refuses to be executed at all once every capability is dropped.

### DNS cache (nscd)

Uptime Kuma 2.x dropped the in-app DNS cache for HTTP monitors and ships `nscd` inside the image instead, started through `sudo`. This role drops every container capability, which leaves that `sudo` unable to elevate: the container logs `Failed to start nscd` on every start, and monitors resolve without a local cache.

## Troubleshooting

### Check the service's logs

You can find the logs in [systemd-journald](https://www.freedesktop.org/software/systemd/man/systemd-journald.service.html) by logging in to the server with SSH and running `journalctl -fu uptime-kuma` (or how you/your playbook named the service, e.g. `mash-uptime-kuma`).
