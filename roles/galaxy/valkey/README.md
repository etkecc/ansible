# Valkey Ansible role

This is an [Ansible](https://www.ansible.com/) role which installs [Valkey](https://valkey.io/) to run as a [Docker](https://www.docker.com/) container wrapped in a systemd service.

This role *implicitly* depends on:

- [`com.devture.ansible.role.playbook_help`](https://github.com/devture/com.devture.ansible.role.playbook_help)
- [`com.devture.ansible.role.systemd_docker_base`](https://github.com/devture/com.devture.ansible.role.systemd_docker_base)
- (optional) [`com.devture.ansible.role.playbook_runtime_messages`](https://github.com/devture/com.devture.ansible.role.playbook_runtime_messages)

Check [defaults/main.yml](defaults/main.yml) for the full list of supported options.
