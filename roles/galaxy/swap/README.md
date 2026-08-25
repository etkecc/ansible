<!--
SPDX-FileCopyrightText: 2022 etke.cc
SPDX-FileCopyrightText: 2026 Slavi Pantaleev

SPDX-License-Identifier: GPL-3.0-or-later
-->

# system/swap

That role creates swap file and configures system to mount it and use automatically

## prerequisites

vars:

```yaml
system_swap_enabled: true
```

> **NOTE**: check [defaults/main.yml](./defaults/main.yml) to see full list of config options

## Notes

- **Changing `system_swap_size` on a host that already has a swap file does nothing.** The role only creates the file when it is not there yet, on purpose: rewriting a swap file that the kernel is currently using would corrupt it. To resize, set `system_swap_enabled: false` and run the playbook (which removes the file and its `/etc/fstab` entry), then set the new size and turn it back on.
- **Turning swap off does not undo `system_swap_sysctl`.** `system_swap_enabled: false` removes the swap file and its `/etc/fstab` entry, but `/etc/sysctl.d/99-swap.conf` — and therefore `vm.swappiness` — is left as the last run set it.

## Testing

This role has a [Molecule](https://ansible.readthedocs.io/projects/molecule/) test suite. See [molecule/README.md](./molecule/README.md), which also explains what such a suite can and cannot prove about a role that manages kernel swap from inside a container.
