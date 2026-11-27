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

# Setting up Matrix.to

This is an [Ansible](https://www.ansible.com/) role which installs [Matrix.to](https://github.com/matrix-org/matrix.to) to run as a [Docker](https://www.docker.com/) container wrapped in a systemd service.

Matrix.to is a redirection service for the Matrix ecosystem which enables users to share links to Matrix entities freely.

See the project's [documentation](https://github.com/matrix-org/matrix.to/blob/main/README.md) to learn what Matrix.to does and why it might be useful to you.

## Adjusting the playbook configuration

To enable Matrix.to with this role, add the following configuration to your `vars.yml` file.

**Note**: the path should be something like `inventory/host_vars/mash.example.com/vars.yml` if you use the [MASH Ansible playbook](https://github.com/mother-of-all-self-hosting/mash-playbook).

```yaml
########################################################################
#                                                                      #
# matrixto                                                             #
#                                                                      #
########################################################################

matrixto_enabled: true

########################################################################
#                                                                      #
# /matrixto                                                            #
#                                                                      #
########################################################################
```

### Set the hostname

To enable Matrix.to you need to set the hostname as well. To do so, add the following configuration to your `vars.yml` file. Make sure to replace `example.com` with your own value.

```yaml
matrixto_hostname: "example.com"
```

After adjusting the hostname, make sure to adjust your DNS records to point the domain to your server.

**Note**: hosting Matrix.to under a subpath (by configuring the `matrixto_path_prefix` variable) does not seem to be possible due to Matrix.to's technical limitations.

## Installing

After configuring the playbook, run the installation command of your playbook as below:

```sh
ansible-playbook -i inventory/hosts setup.yml --tags=setup-all,start
```

If you use the MASH playbook, the shortcut commands with the [`just` program](https://github.com/mother-of-all-self-hosting/mash-playbook/blob/main/docs/just.md) are also available: `just install-all` or `just setup-all`

## Usage

After running the command for installation, Matrix.to becomes available at the specified hostname like `https://example.com`.

## Troubleshooting

### Check the service's logs

You can find the logs in [systemd-journald](https://www.freedesktop.org/software/systemd/man/systemd-journald.service.html) by logging in to the server with SSH and running `journalctl -fu matrixto` (or how you/your playbook named the service, e.g. `mash-matrixto`).
