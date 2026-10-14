<!--
SPDX-FileCopyrightText: 2022 etke.cc
SPDX-FileCopyrightText: 2026 Slavi Pantaleev
SPDX-FileCopyrightText: 2026 spatterlight

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Swap Ansible role

This is an [Ansible](https://www.ansible.com/) role which manages [swap](https://wiki.archlinux.org/title/Swap) files on a Linux host.

By default it creates a single 1 GB swap file at `/var/swap`. To change that, or to add more:

```yaml
# The first swap file (size in megabytes)
system_swap_path: /var/swap
system_swap_size: 1024

# Any additional swap files
system_swap_files_custom:
  - path: /mnt/data/swap
    size: 4096
```

Each entry also takes an optional `priority`, and `state: absent` to remove a swap file.

Check [`defaults/main.yml`](defaults/main.yml) for the full list of supported options.

## Limitations

- **The size and the priority of an existing swap file are never changed.** The role only sets a swap file up when it is not there yet, on purpose: rewriting a swap file that the kernel is currently using would corrupt it. To change one, have the role remove it first, then set the new values and run it again.
- **`system_swap_enabled: false` removes every swap file in the lists**, whatever its `state`. It does not undo `system_swap_sysctl`: `/etc/sysctl.d/99-swap.conf` is left as the last run wrote it.
- **A swap file that could not be set up is left as it is.** When a step fails, the role stops working on that swap file, so that one which could not be enabled does not end up in `/etc/fstab`. With `system_swap_ignore_errors: true` it then carries on with the next swap file instead of failing the run. If the file had already been created by then, later runs skip it; delete it by hand to have it set up again.

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

Tags are created by [`.github/workflows/autotag.yml`](.github/workflows/autotag.yml), which asks [`bin/compute-next-tag.sh`](bin/compute-next-tag.sh) what the commit on `main` should be released as. This role deploys no software and has no version of its own, so the answer comes from the tags that already exist: any change under `defaults/`, `files/`, `meta/`, `tasks/` or `templates/` rolls the release counter (`v1.0.0-1`, `v1.0.0-2`, …), and a commit that only touches documentation, CI or the Molecule scenarios is not released at all. A new series is started by tagging one commit by hand, as `v2.0.0-0` say.

[`bin/test-compute-next-tag.sh`](bin/test-compute-next-tag.sh) exercises that script against throwaway repositories, and runs as a prek hook.
