# systemd service manager Ansible role

This is an [Ansible](https://www.ansible.com/) role which manages systemd services.


## Features

- **starting** (restarting) services, in order, according to their `priority`. Services can all be stopped cleanly and then started anew, or they can be restarted one-by-one (see `devture_systemd_service_manager_service_restart_mode`)

- making services **auto-start** (see `devture_systemd_service_manager_services_autostart_enabled`)

- **verifying** services managed to start (see `devture_systemd_service_manager_up_verification_enabled`)

- **stopping** services, in order, according to their `priority`

- starting/stopping all defined services, or a group of services (`--tags=restart-group`, `--tags=stop-group`)

- restarting services by cleanly stopping them and restarting them, or one by one


## Usage

Example playbook:

```yaml
- hosts: servers
  roles:
    - when: devture_systemd_service_manager_enabled | bool
      role: galaxy/com.devture.ansible.role.systemd_service_manager
```

Example playbook configuration (`group_vars/servers` or other):

```yaml
# See `devture_systemd_service_manager_services_list_auto` and `devture_systemd_service_manager_services_list_additional`
devture_systemd_service_manager_services_list_auto: |
  {{
    ([{'name': 'some-service.service', 'priority': 1000}])
    +
    ([{'name': 'another-service.service', 'priority': 1500}])
  }}
```

Example playbook invocations tags (e.g. `ansible-playbook -i inventory/hosts setup.yml --tags=XXXXX`):

- `restart`, `restart-all`, `start-all` - restarts all services and potentially makes them auto-start (depending on `devture_systemd_service_manager_services_autostart_enabled`)

- `restart-group`, `start-group` - restarts services belonging to the specified group (e.g. `--extra-vars="group=core"`)

- `stop`, `stop-all` - stops all services

- `stop-group` - stops services belonging to the specified group (e.g. `--extra-vars="group=core"`)

