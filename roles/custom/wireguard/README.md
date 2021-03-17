# custom/wireguard

A role to install [WireGuard](https://wireguard.com) server

## Requirements & install

1. Put following in your matrix host's vars.yml file:

```yml
# Enable wireguard install
custom_wireguard_enabled: true
# List of clients, format
# [Client 1 name, Client 2 name, etc], eg:
# [Laptop, Phone, Tablet, Desktop]
custom_wireguard_clients: []

```

Run `ansible-playbook play/matrix.yml -t setup-all,start`

## Configuration

> **NOTE**: check [defaults/main.yml](./defaults/main.yml) to see full list of config options

custom_wireguard_enabled: false
custom_wireguard_interface_net: eth0
custom_wireguard_interface: wg0
custom_wireguard_overwrite: true
custom_wireguard_subnet: 10.200.200
custom_wireguard_dns: ['1.1.1.1', '1.0.0.1']
custom_wireguard_port: '51820'
custom_wireguard_path: /etc/wireguard
custom_wireguard_clients: []
### custom_wireguard_enabled

Enable role, default: `false`

### custom_wireguard_interface_net

Server public internet interface, default: `eth0`

### custom_wireguard_interface

WireGuard interface name, default: `wg0`

### custom_wireguard_overwrite

Overwrite config files (NOT keys, they are preserved) on each role run, default: `true`

### custom_wireguard_subnet

Subnet for wireguard peers, default: `10.200.200`

### custom_wireguard_dns

DNS servers to set on wireguard peers, default: `['1.1.1.1', '1.0.0.1']`

### custom_wireguard_port

WireGuard server port, default: '51820'

### custom_wireguard_clients

List of clients, eg: `['laptop', 'phone', 'desktop']`
