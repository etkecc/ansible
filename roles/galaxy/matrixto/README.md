<!--
SPDX-FileCopyrightText: 2023 Slavi Pantaleev
SPDX-FileCopyrightText: 2025, 2026 Suguru Hirahara

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# Matrix.to Ansible role

This is an [Ansible](https://www.ansible.com/) role which installs [Matrix.to](https://github.com/matrix-org/matrix.to) to run as a [Docker](https://www.docker.com/) container wrapped in a systemd service.

This role *implicitly* depends on:

- [`com.devture.ansible.role.playbook_help`](https://github.com/devture/com.devture.ansible.role.playbook_help)
- [`com.devture.ansible.role.systemd_docker_base`](https://github.com/devture/com.devture.ansible.role.systemd_docker_base)

Check [`defaults/main.yml`](defaults/main.yml) for the full list of supported options. Refer to [this page](docs/configuring-docmost.md) for details about setting up the service with this role.

💡 For an Ansible playbook which integrates this role and makes it easier to use, see the [Mother-of-All-Self-Hosting Ansible playbook](https://github.com/mother-of-all-self-hosting/mash-playbook).

## Development

Please refer to [this page](https://github.com/mother-of-all-self-hosting/mash-playbook/blob/main/docs/developer-documentation.md) on the MASH playbook for general guidelines about development.

### Collaborating on Radicle

This repository can be cloned from the [Radicle](https://radicle.dev) network, a peer-to-peer code collaboration stack built on Git. Please follow [this "Getting Started" guide](https://radicle.dev/guides/quick-start) on the official documentation for the basic installation and usage of the Radicle toolchain. You might also want to take a look at [Radicle Desktop](https://radicle.network/desktop) for simple collaboration.

You can clone the repository by running the command below:

```sh
rad clone rad:z2f6KBw91HXLTLiqchB2R9R5DQiPs
```

💡 When you only want to "seed" a repository and have no interest in contributing code, you can still be a repository’s friend with the `rad seed` command. This is Radicle’s version of a ⭐ *star* or 👍 *like*, where you care by sharing it with others on the network.

### pre-commit

You can optionally install a Git pre-commit hook (via [mise](https://mise.jdx.dev/) + [prek](https://prek.j178.dev/)) that runs formatting and linting checks before each commit. See [`.pre-commit-config.yaml`](./.pre-commit-config.yaml) for which hooks are to be executed.

To install the hook, run the [`just`](https://github.com/casey/just) command below:

```sh
just prek-install-git-pre-commit-hook
```
