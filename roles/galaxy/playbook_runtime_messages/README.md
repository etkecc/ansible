# Ansible playbook runtime messages role

This is an Ansible role which lets other roles inject messages into `devture_playbook_runtime_messages_list` and outputs those messages at the end of playbook execution.

## Usage

Example playbook:

```yaml
- hosts: servers
  roles:
    - role: some_role
    - role: another_role

    - role: galaxy/com.devture.ansible.role.playbook_runtime_messages
```

Example tasks in `some_role` or `another_role`:

```yaml
- name: Inject warning message
  ansible.builtin.set_fact:
    devture_playbook_runtime_messages_list: |
      {{
        devture_playbook_runtime_messages_list | default([])
        +
        [
          "NOTE: This is a warning message to be printed at the end of playbook execution"
        ]
      }}
```
