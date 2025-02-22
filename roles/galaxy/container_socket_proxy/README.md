# Container Socket Proxy Ansible role

This is an [Ansible](https://www.ansible.com/) role which installs [docker-socket-proxy](https://github.com/Tecnativa/docker-socket-proxy) to run as a [Docker](https://www.docker.com/) container wrapped in a systemd service.

This role *implicitly* depends on the [`com.devture.ansible.role.systemd_docker_base` role](https://github.com/devture/com.devture.ansible.role.systemd_docker_base).

May be used in combination with the [`ansible-role-traefik` role](https://github.com/mother-of-all-self-hosting/ansible-role-traefik).
