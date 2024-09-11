# prometheus_node_exporter

This is an [Ansible](https://www.ansible.com/) role which installs [Prometheus node exporter](https://github.com/prometheus/node_exporter) to run as a [Docker](https://www.docker.com/) container wrapped in a systemd service.

This role *implicitly* depends on:

- [`com.devture.ansible.role.playbook_help`](https://github.com/devture/com.devture.ansible.role.playbook_help)
- [`com.devture.ansible.role.systemd_docker_base`](https://github.com/devture/com.devture.ansible.role.systemd_docker_base)


> **NOTE**: check [defaults/main.yml](./defaults/main.yml) to see full list of config options
