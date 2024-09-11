# Docker SDK for Python Ansible role

This is an Ansible role which installs the [Docker SDK for Python](https://pypi.org/project/docker/) on various distros.

This role aims to install the Docker SDK using the distro's official package manager, not via `pip`, etc.

## Usage

Example playbook:

```yaml
- hosts: servers

  roles:
    - when: devture_docker_sdk_for_python_installation_enabled | bool
      role: galaxy/com.devture.ansible.role.docker_sdk_for_python
      # Uncomment to make it run on some tags only, not always
      # tags:
      #  - setup-all
```
