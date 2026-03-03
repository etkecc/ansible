<!--
SPDX-FileCopyrightText: 2018 - 2025 Slavi Pantaleev
SPDX-FileCopyrightText: 2019 Eduardo Beltrame
SPDX-FileCopyrightText: 2020 - 2025 MDAD project contributors
SPDX-FileCopyrightText: 2024 - 2025 Suguru Hirahara

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# Setting up LiveKit Server

This is an [Ansible](https://www.ansible.com/) role which installs [LiveKit Server](https://docs.livekit.io/home/) to run as a [Docker](https://www.docker.com/) container wrapped in a systemd service.

> LiveKit is an open source platform for developers building realtime media applications. It makes it easy to integrate audio, video, text, data, and AI models while offering scalable realtime infrastructure built on top of WebRTC.

<small>Refer: https://docs.livekit.io/home/get-started/intro-to-livekit/</small>

## Prerequisites

### Adjusting firewall rules

To ensure LiveKit Server functions correctly, the following firewall rules and port forwarding settings are required:

- `7881/tcp`: ICE/TCP
- `7882/udp`: ICE/UDP Mux

When embedded TURN is enabled (`livekit_server_config_turn_enabled: true`), open these as well:

- `livekit_server_config_turn_udp_port/udp` (default: `3478/udp`): TURN/UDP
- `livekit_server_config_turn_tls_port/tcp` (default: `5349/tcp`): TURN/TLS (direct mode)
- `livekit_server_config_turn_relay_range_start-livekit_server_config_turn_relay_range_end/udp` (default: `30000-30020/udp`): TURN relay ports

💡 The suggestions above are inspired by the upstream [Ports and Firewall](https://docs.livekit.io/home/self-hosting/ports-firewall/) documentation based on how LiveKit is configured in the role. If you're using custom configuration, adjust the firewall rules and port forwarding accordingly.

### Host networking mode

Setting `livekit_server_container_network: host` runs LiveKit with host networking.

- Docker port publishing (`-p`) is skipped in this mode.
- You need to open firewall ports directly on the host.
- This can improve performance and startup time when using larger UDP ranges, but reduces container-network isolation.

## Adjusting the playbook configuration

To enable LiveKit Server with this role, add the following configuration to your `vars.yml` file.

**Notes**: if you use the [matrix-docker-ansible-deploy (MDAD)](https://github.com/spantaleev/matrix-docker-ansible-deploy) Ansible playbook, you do not need to enable LiveKit Server explicitly as it is automatically enabled when [Element Call](https://github.com/element-hq/element-call) is enabled.

```yaml
########################################################################
#                                                                      #
# livekit-server                                                       #
#                                                                      #
########################################################################

livekit_server_enabled: true

########################################################################
#                                                                      #
# /livekit-server                                                      #
#                                                                      #
########################################################################
```

### Set the hostname

To serve LiveKit Server you need to set the hostname as well. To do so, add the following configuration to your `vars.yml` file. Make sure to replace `example.com` with your own value.

```yaml
livekit_server_hostname: "example.com"
```

### Set the key

You also would probably wish to add at least one key to the `livekit_server_config_keys_custom` variable.

To add your own key, add the following configuration to your `vars.yml` file (adapt to your needs).

```yaml
livekit_server_config_keys_custom:
  key1: secret1
  key2: secret2
```

**Note**: on the MDAD playbook, the key value is specified with `livekit_server_config_keys_auto` by default, so you do not need to add them. See its [`matrix_servers`](https://github.com/spantaleev/matrix-docker-ansible-deploy/blob/master/group_vars/matrix_servers) for details.

### TURN TLS modes

`livekit_server_config_turn_external_tls` controls where TURN TLS is terminated.

The default in this role is `false`.

- Set it to `true` when a reverse proxy (such as Traefik) terminates TURN TLS and forwards plain TCP to LiveKit.
- Set it to `false` when LiveKit should terminate TLS itself. In this mode, set `livekit_server_config_turn_cert_file` and `livekit_server_config_turn_key_file` to valid file paths (defaults are empty).

When external TLS mode is enabled, the role expects Traefik TCP labels to be set (`livekit_server_container_labels_turn_traefik_enabled: true` and a non-empty `livekit_server_container_labels_turn_traefik_entrypoints`) and does not configure cert files for TURN.

### Limitations

LiveKit Server's TURN listener behavior depends on where TLS is terminated:

- Direct LiveKit TURN listeners (`livekit_server_config_turn_external_tls: false`) still use IPv4-only sockets for `3479/udp` and `5350/tcp`, so IPv6 connectivity to these endpoints is not possible.
- With [external TLS mode](#turn-tls-modes) (`livekit_server_config_turn_external_tls: true`), the reverse proxy (for example Traefik) can provide IPv6-facing endpoints and forward TURN/TCP to LiveKit.

LiveKit appears to intentionally only listen on `udp4` and `tcp4` in direct mode, as seen in [TURN UDP listener code](https://github.com/livekit/livekit/blob/154b4d26b769c68a03c096124094b97bf61a996f/pkg/service/turn.go#L128) and [TURN TCP listener code](https://github.com/livekit/livekit/blob/154b4d26b769c68a03c096124094b97bf61a996f/pkg/service/turn.go#L92).

## Installing

After configuring the playbook, run the installation command of your playbook as below:

```sh
ansible-playbook -i inventory/hosts setup.yml --tags=setup-all,start
```

If you use the MDAD Ansible playbook, the shortcut commands with the [`just` program](https://github.com/spantaleev/matrix-docker-ansible-deploy/blob/master/docs/just.md) are also available: `just install-all` or `just setup-all`

## Troubleshooting

You can find the logs in [systemd-journald](https://www.freedesktop.org/software/systemd/man/systemd-journald.service.html) by logging in to the server with SSH and running `journalctl -fu livekit-server` (or how you/your playbook named the service, e.g. `matrix-livekit-server`).

### Increase logging verbosity

The default logging level for this component is `info`. If you want to increase the verbosity, add the following configuration to your `vars.yml` file and re-run the playbook:

```yaml
# Valid values: debug, info, warn, error
livekit_server_config_logging_level: "debug"
```
