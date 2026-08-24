<!--
SPDX-FileCopyrightText: 2023 - 2026 Aine
SPDX-FileCopyrightText: 2026 Slavi Pantaleev

SPDX-License-Identifier: GPL-3.0-or-later
-->

# fail2ban Ansible role

This is an [Ansible](https://www.ansible.com/) role which manages [fail2ban](https://github.com/fail2ban/fail2ban) on a Linux host. fail2ban watches log files for authentication failures and bans the addresses behind them by adding firewall rules.

Unlike most other roles in this collection, this one does not run a container. It installs the `fail2ban` package from the distribution's package repository, writes `/etc/fail2ban/jail.local` and runs the daemon on the host itself. There is no version to pin: whichever fail2ban the distribution ships is the one you get.

Out of the box the role enables fail2ban's `sshd` jail and nothing else. Everything beyond that goes into `system_security_fail2ban_configuration_extension`, which is appended verbatim to `jail.local`, so any jail, filter or action fail2ban understands can be configured through it.

On Debian and Ubuntu, fail2ban bans through `nftables` and the `sshd` jail reads the systemd journal. Both are the distribution package's own defaults, not something this role sets.

## Options

- `system_security_fail2ban_enabled` (bool, default: `true`)

  Whether the role does anything at all. When `false`, the role installs nothing, writes nothing and starts nothing. It does **not** uninstall or stop an already-installed fail2ban.

- `system_security_fail2ban_sshd_port` (int/string, default: `22`)

  The port the `sshd` jail watches and bans on. Set this if SSH does not listen on 22, otherwise bans will be installed for a port nobody is attacking.

- `system_security_fail2ban_ignoreip` (string, default: `'127.0.0.1/8 ::1'`)

  IPs, CIDRs, or DNS names fail2ban never bans, space- or comma-separated. Set real infrastructure hosts (VPN, control, monitoring) here via group vars; the default covers loopback only.

- `system_security_fail2ban_bantime_increment` (bool, default: `true`)

  Escalates the ban duration for repeat offenders, backed by fail2ban's database. It only ever extends the ban of an already-banned address, so anything in `system_security_fail2ban_ignoreip` is never affected.

- `system_security_fail2ban_configuration_extension` (string, default: `''`)

  Appended to `/etc/fail2ban/jail.local` as-is. Use it to enable additional jails or to override anything fail2ban puts in `[DEFAULT]`.

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

### Releases

Pushing to `main` tags a release automatically, if the commit changed anything under `defaults/`, `handlers/`, `meta/`, `tasks/` or `templates/`. Tags look like `v1.0.0-1`: the version half is a statement about this role's own interface and only a human changes it (by tagging, say, `v2.0.0-0` by hand), while the release counter after the dash is incremented automatically. See [`bin/compute-next-tag.sh`](bin/compute-next-tag.sh) for the full reasoning.
