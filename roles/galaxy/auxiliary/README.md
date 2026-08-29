<!--
SPDX-FileCopyrightText: 2023 Slavi Pantaleev
SPDX-FileCopyrightText: 2026 Suguru Hirahara

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# AUX Ansible role

This is an [Ansible](https://www.ansible.com/) role which helps you manage auxiliary files and directories.

Check [`defaults/main.yml`](defaults/main.yml) for the full list of supported options.

💡 For an Ansible playbook which integrates this role and makes it easier to use, see the [Mother-of-All-Self-Hosting Ansible playbook](https://github.com/mother-of-all-self-hosting/mash-playbook).

## Testing

The role ships a [Molecule](https://ansible.readthedocs.io/projects/molecule/) suite which runs it against a container, hands it a representative set of directory, file, package and command definitions and then reads the host back. See [`molecule/README.md`](molecule/README.md) for what it asserts and for what it deliberately does not.

## Releases

Release tags are computed from the state of the repository rather than from commit messages: [`bin/compute-next-tag.sh`](bin/compute-next-tag.sh) continues the newest existing release series and moves only the `-N` counter, and only when a commit touched something a consumer of this role can see (`defaults/`, `meta/`, `tasks/`, and `files/`/`templates/` should they ever appear). Documentation, CI and test changes are deliberately not released, so that the playbooks pinning this role are not churned for nothing.

This role has no version of its own — it deploys no software — so the version part of the tag is inherited from whatever came before. A breaking change to its variables is released by tagging one commit by hand as the start of a new series (`v2.0.0-0`, say); everything after it continues from there. [`bin/test-compute-next-tag.sh`](bin/test-compute-next-tag.sh) exercises all of this against throwaway repositories, and runs as a pre-commit hook.

## Upgrading from v1 to v2

Version 2 displays non-empty stdout and stderr from successful `aux_command_definitions` by default. This improves routine command visibility but can expose sensitive data printed by a command. Set `aux_command_default_show_output: false` to preserve the v1 behavior globally, or add `show_output: false` to individual command definitions whose output must remain hidden.

## Development

You can optionally install a Git pre-commit hook (via [mise](https://mise.jdx.dev/) + [prek](https://prek.j178.dev/)) that runs formatting and linting checks before each commit. See [`.pre-commit-config.yaml`](./.pre-commit-config.yaml) for which hooks are to be executed.

To install the hook, run the [`just`](https://github.com/casey/just) command below:

```sh
just prek-install-git-pre-commit-hook
```
