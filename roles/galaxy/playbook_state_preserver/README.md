# Ansible playbook state preserver role

This is an Ansible role which preserves (backs up) the `vars.yml` file and playbook git commit hash to the server. It supersedes the `com.devture.ansible.role.vars_preserver` role which only did the former.

This role *implicitly* depends on the `com.devture.ansible.role.playbook_runtime_messages` role.

## Usage

Example playbook:

```yaml
- hosts: servers
  roles:
    - when: devture_playbook_state_preserver_enabled | bool
      role: galaxy/com.devture.ansible.role.playbook_state_preserver
      # Uncomment to make it run on some tags only, not always
      # tags:
      #  - setup-all
```

Example configuration (see `defaults/main.yml` for more):

```yaml
devture_playbook_state_preserver_uid: 1000
devture_playbook_state_preserver_gid: 1000

devture_playbook_state_preserver_vars_preservation_dst: /path/on-server/to/vars.yml

devture_playbook_state_preserver_commit_hash_preservation_dst: /path/on-server/to/git_hash.yml
```
