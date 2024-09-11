# Timesync Ansible role

This is an Ansible role which installs `systemd-timesyncd` or `ntpd`, depending on the distro.

## Usage

Example playbook:

```yaml
- hosts: servers

  roles:
    - when: devture_timesync_installation_enabled | bool
      role: galaxy/com.devture.ansible.role.timesync
      # Uncomment to make it run on some tags only, not always
      # tags:
      #  - setup-all
      #  - setup-timesync
```
