<!--
SPDX-FileCopyrightText: 2023 Aine
SPDX-FileCopyrightText: 2026 Slavi Pantaleev

SPDX-License-Identifier: GPL-3.0-or-later
-->

# ufw Ansible role

This is an [Ansible](https://www.ansible.com/) role which manages the [Uncomplicated Firewall (ufw)](https://launchpad.net/ufw) of a Linux host.

Unlike most other roles in this collection, this one does not run a container. It installs the `ufw` package from the distribution's package repository, applies firewall rules to the host itself and enables the firewall.

Rules are assembled from 3 lists, in this order:

- `system_security_ufw_rules_base` — rules that the role considers essential (HTTP/HTTPS). You most likely do not want to change these.
- `system_security_ufw_rules_auto` — rules contributed by a playbook or a group, depending on which services are enabled. You most likely do not want to set these yourself.
- `system_security_ufw_rules_custom` — rules of your own. **This is the variable you want.**

Each rule is a dictionary with `name` (used as the ufw comment), `rule`, `port` and `proto` keys, and optional `from` and `delete` keys. Setting `delete: true` removes a rule that was previously applied.

Because the role operates on the host itself and not on a container, an incorrect rule set can lock you out of the machine. SSH access is therefore handled separately, via `system_security_ufw_ssh_allowed` and `system_security_ssh_port`.

Check [`defaults/main.yml`](defaults/main.yml) for the full list of supported options.

💡 For an Ansible playbook which integrates this role and makes it easier to use, see the [Mother-of-All-Self-Hosting Ansible playbook](https://github.com/mother-of-all-self-hosting/mash-playbook).

## Development

### pre-commit

You can optionally install a Git pre-commit hook (via [mise](https://mise.jdx.dev/) + [prek](https://prek.j178.dev/)) that runs formatting and linting checks before each commit. See [`.pre-commit-config.yaml`](./.pre-commit-config.yaml) for which hooks are to be executed.

To install the hook, run the [`just`](https://github.com/casey/just) command below:

```sh
just prek-install-git-pre-commit-hook
```

### Molecule

This role supports [Molecule](https://docs.ansible.com/projects/molecule/), an Ansible testing framework designed for developing and testing Ansible collections, playbooks, and roles.

Refer to [this page](./molecule/README.md) for details about how to utilize it.
