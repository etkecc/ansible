<!--
SPDX-FileCopyrightText: 2022 etke.cc
SPDX-FileCopyrightText: 2026 Slavi Pantaleev

SPDX-License-Identifier: GPL-3.0-or-later
-->

# system/cleanup

System cleanup role

Refer to `defaults/main.yml` to get the list of options

## Docker cleanup

`system_cleanup_docker` installs a script (`/system-cleanup/bin/cleanup-docker` by default) which removes:

- **superseded images**: unused images for which a newer image of the same repository arrived at least 3 days ago (`system_cleanup_docker_config_superseded_images_grace_period_days`). Unlike `docker image prune -a`, unused images without a newer version (stopped services, timer-only containers, locally built images) are kept.
- **stopped containers**
- **anonymous volumes**, only if `system_cleanup_docker_config_remove_anonymous_volumes` is on

Networks and named volumes are never removed.

Ansible runs the script on runs tagged `start` (e.g. `just setup-all`). With `system_cleanup_docker_timer_enabled`, a systemd timer also runs it on a schedule. You can also run it by hand, with `--dry-run` to only see what it would remove.

On the legacy overlay2 graph driver, Docker does not record when an image was pulled, so the build time is used instead, which shortens the grace period for pulled images.

**Upgrading:** earlier versions ran `docker image prune -a` and `docker volume prune`. To get closer to that, set `system_cleanup_docker_config_superseded_images_grace_period_days: 0` and `system_cleanup_docker_config_remove_anonymous_volumes: true`.

## Upgrading to v2

- The Docker cleanup changed as described above.
- The journald autovacuum timer (`journalctl --vacuum-time=7d`) is now off by default and gets removed. Earlier versions installed it on every host, ignoring `system_cleanup_logs`. To keep it, set `system_cleanup_logs: true`.
- `purge-old-kernels` moved from `/usr/local/bin` to `system_cleanup_bin_path`.

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
