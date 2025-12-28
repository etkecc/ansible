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
SPDX-FileCopyrightText: 2023 Pierre 'McFly' Marty
SPDX-FileCopyrightText: 2024 Tiz
SPDX-FileCopyrightText: 2024 - 2025 Suguru Hirahara

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# Setting up LanguageTool

This is an [Ansible](https://www.ansible.com/) role which installs [LanguageTool](https://languagetool.org) to run as a [Docker](https://www.docker.com/) container wrapped in a systemd service.

LanguageTool is an open source online grammar, style and spell checker.

See the project's [documentation](https://languagetool.org/dev) to learn what LanguageTool does and why it might be useful to you.

## Adjusting the playbook configuration

To enable LanguageTool with this role, add the following configuration to your `vars.yml` file.

**Note**: the path should be something like `inventory/host_vars/mash.example.com/vars.yml` if you use the [MASH Ansible playbook](https://github.com/mother-of-all-self-hosting/mash-playbook).

```yaml
########################################################################
#                                                                      #
# languagetool                                                         #
#                                                                      #
########################################################################

languagetool_enabled: true

########################################################################
#                                                                      #
# /languagetool                                                        #
#                                                                      #
########################################################################
```

### Set the hostname

To enable LanguageTool you need to set the hostname as well. To do so, add the following configuration to your `vars.yml` file. Make sure to replace `example.com` with your own value.

```yaml
languagetool_hostname: "example.com"
```

After adjusting the hostname, make sure to adjust your DNS records to point the domain to your server.

### Enable n-gram data (optional)

LanguageTool can make use of large n-gram data sets to detect errors with words that are often confused, like "their" and "there". See [*Finding errors using n-gram data*](https://dev.languagetool.org/finding-errors-using-n-gram-data) to learn more.

>[!NOTE]
> The n-gram data set is huge and thus not enabled by default.

To make use of it with your own LanguageTool server, you may enable n-gram data and choose which languages' n-gram data to download by adding the following configuration to your `vars.yml` file:

```yaml
languagetool_ngrams_enabled: true

languagetool_ngrams_langs_enabled: ['fr', 'en']
```

Check the `languagetool_ngrams_langs` variable on [`default/main.yml`](https://github.com/mother-of-all-self-hosting/ansible-role-languagetool/blob/main/defaults/main.yml) for a list of languages for which the Ansible role supports downloading n-gram data.

Additional languages which are not defined on the role may be available. You can redefine `languagetool_ngrams_langs` to have the role download URL for those languages.

## Installing

After configuring the playbook, run the installation command of your playbook as below:

```sh
ansible-playbook -i inventory/hosts setup.yml --tags=setup-all,start
```

If you use the MASH playbook, the shortcut commands with the [`just` program](https://github.com/mother-of-all-self-hosting/mash-playbook/blob/main/docs/just.md) are also available: `just install-all` or `just setup-all`

## Usage

After running the command for installation, the LanguageTool instance becomes available at the URL specified with `languagetool_hostname` and `languagetool_path_prefix`. With the configuration above, the service is hosted at `https://example.com`.

You can test the instance by making a request to [LanguageTool's HTTP API](https://dev.languagetool.org/public-http-api) by running a *curl* command as follows: `curl --data "language=en-US&text=a simple test" https://example.com/languagetool/v2/check`

There are [software that support LanguageTool as an add-on](https://dev.languagetool.org/software-that-supports-languagetool-as-a-plug-in-or-add-on). To use them with your instance, set `https://example.com/languagetool/v2` to the URL (assuming you've installed at the `/languagetool` path prefix).

## Troubleshooting

### Check the service's logs

You can find the logs in [systemd-journald](https://www.freedesktop.org/software/systemd/man/systemd-journald.service.html) by logging in to the server with SSH and running `journalctl -fu languagetool` (or how you/your playbook named the service, e.g. `mash-languagetool`).
