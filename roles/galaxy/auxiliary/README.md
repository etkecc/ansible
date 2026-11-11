<!--
SPDX-FileCopyrightText: 2023 Slavi Pantaleev
SPDX-FileCopyrightText: 2026 Suguru Hirahara

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# AUX Ansible role

This is an [Ansible](https://www.ansible.com/) role which helps you manage auxiliary files and directories.

Check [`defaults/main.yml`](defaults/main.yml) for the full list of supported options.

💡 For an Ansible playbook which integrates this role and makes it easier to use, see the [Mother-of-All-Self-Hosting Ansible playbook](https://github.com/mother-of-all-self-hosting/mash-playbook).

## Upgrading from v1 to v2

Version 2 displays non-empty stdout and stderr from successful `aux_command_definitions` by default. This improves routine command visibility but can expose sensitive data printed by a command. Set `aux_command_default_show_output: false` to preserve the v1 behavior globally, or add `show_output: false` to individual command definitions whose output must remain hidden.

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

### Releases

Tags are computed from the state of the repository rather than from commit messages: [`bin/compute-next-tag.sh`](bin/compute-next-tag.sh) continues the release series of the newest existing tag whenever a commit touches `defaults/`, `files/`, `meta/`, `tasks/` or `templates/`, and the [autotag workflow](.github/workflows/autotag.yml) pushes the result. Commits which only touch documentation, CI configuration or the test suite are not released.

This role deploys no software and so has no version of its own; the version component of the tags is a number chosen by hand. To open a new series — for a breaking change to the role's variables, say — tag one commit as `v2.0.0-0` by hand, and everything after it continues from there.

[`bin/test-compute-next-tag.sh`](bin/test-compute-next-tag.sh) exercises that script against throwaway repositories, and runs as a prek hook.
