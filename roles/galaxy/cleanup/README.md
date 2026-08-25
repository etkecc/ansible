<!--
SPDX-FileCopyrightText: 2022 etke.cc
SPDX-FileCopyrightText: 2026 Slavi Pantaleev

SPDX-License-Identifier: GPL-3.0-or-later
-->

# system/cleanup

System cleanup role

Refer to `defaults/main.yml` to get the list of options

Note that the Docker pruning enabled by `system_cleanup_docker` only runs when `start` is among the tags the playbook was invoked with — which is what mash-playbook's `just setup-all` (`--tags=setup-all,start`) and `just install-all` (`--tags=install-all,start`) pass. A run without that tag, such as `just install-service <name>`, installs and schedules everything else but prunes nothing.

## Testing

The role has a [Molecule](https://ansible.readthedocs.io/projects/molecule/) test suite. See [`molecule/README.md`](./molecule/README.md) for what it covers, what it deliberately does not, and how to run it.

## Releases

Tags are computed from the state of the repository rather than from commit messages: [`bin/compute-next-tag.sh`](./bin/compute-next-tag.sh) continues the release series of the newest existing tag whenever a commit touches `defaults/`, `files/`, `meta/`, `tasks/` or `templates/`, and the [autotag workflow](./.github/workflows/autotag.yml) pushes the result. Commits which only touch documentation, CI configuration or the test suite are not released.

This role deploys no software and so has no version of its own; the version component of the tags is a number chosen by hand. To open a new series — for a breaking change to the role's variables, say — tag one commit as `v2.0.0-0` by hand, and everything after it continues from there.

## Development

You can optionally install a Git pre-commit hook (via [mise](https://mise.jdx.dev/) + [prek](https://prek.j178.dev/)) that runs formatting and linting checks before each commit. See [`.pre-commit-config.yaml`](./.pre-commit-config.yaml) for which hooks are to be executed.

To install the hook, run the [`just`](https://github.com/casey/just) command below:

```sh
just prek-install-git-pre-commit-hook
```
