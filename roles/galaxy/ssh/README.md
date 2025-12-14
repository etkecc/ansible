# system/security/ssh

This role manages **OpenSSH server (sshd)** configuration and **authorized / unauthorized SSH keys**.
It is primarily focused on **security hardening** while still allowing controlled exceptions for specific workflows (for example, port forwarding or tunnels).

> **NOTE**: See [`defaults/main.yml`](./defaults/main.yml) for the authoritative and complete list of supported variables and their default values.

---

## Overview

When enabled, this role:

* Applies a hardened `sshd_config` based on configurable defaults
* Manages SSH service name differences across distributions
* Controls authentication methods, forwarding features, crypto settings, and session behavior
* Manages authorized and revoked SSH public keys

---

## Core options

### Enable / service handling

* `system_security_ssh_enabled` (bool, default: `true`)

  * Enables or disables SSH hardening managed by this role.

* `system_security_ssh_services` (list, default: `["sshd", "ssh"]`)

  * Possible SSH service names to manage (distribution-dependent).

* `system_security_ssh_port` (int, default: `22`)

  * SSH daemon listening port.

---

## Authentication & access control

* `system_security_ssh_pubkey_authentication` (bool, default: `true`)

  * Enables or disables public key authentication.

* `system_security_ssh_password_authentication` (bool, default: `false`)

  * Enables or disables password authentication.

* `system_security_ssh_challenge_response_authentication` (bool, default: `false`)

  * Controls challenge-response authentication (for example, OTP-based auth).

* `system_security_ssh_permit_empty_passwords` (bool, default: `false`)

  * Allows or blocks empty passwords.

* `system_security_ssh_permit_root_login` (bool, default: `true`)

  * Controls root login over SSH.

* `system_security_ssh_max_auth_tries` (int, default: `3`)

  * Maximum number of authentication attempts per connection.

---

## Session & connection behavior

* `system_security_ssh_login_grace_time` (int, default: `0`)

  * Time (in seconds) allowed for successful login before disconnect.

* `system_security_ssh_client_alive_interval` (int, default: `120`)

  * Interval (in seconds) for keepalive messages.

* `system_security_ssh_use_dns` (bool, default: `false`)

  * Enables or disables DNS lookups for incoming connections.

* `system_security_ssh_use_pam` (bool, default: `true`)

  * Enables or disables PAM integration.

---

## Forwarding, tunnels & graphical access

These options are **disabled by default** to reduce attack surface.

* `system_security_ssh_allow_tcp_forwarding` (bool, default: `false`)

  * Controls `AllowTcpForwarding`.
  * Enable this if you rely on:

    * SSH local or remote port forwarding
    * VS Code Remote / Remote Tunnels

* `system_security_ssh_allow_streamlocal_forwarding` (bool, default: `false`)

  * Controls `AllowStreamLocalForwarding`.

* `system_security_ssh_gateway_ports` (bool, default: `false`)

  * Controls `GatewayPorts`.

* `system_security_ssh_permit_tunnel` (bool, default: `false`)

  * Controls `PermitTunnel`.

* `system_security_ssh_x11_forwarding` (bool, default: `false`)

  * Enables or disables X11 forwarding.

---

## Environment, logging & UX

* `system_security_ssh_accept_env` (string, default: `'LANG LC_*'`)

  * Environment variables accepted from the client.

* `system_security_ssh_print_last_log` (bool, default: `true`)

  * Shows last login information on successful login.

* `system_security_ssh_print_motd` (bool, default: `false`)

  * Enables or disables MOTD printing.

* `system_security_ssh_compression` (bool, default: `false`)

  * Enables or disables SSH compression.

---

## Crypto & protocol hardening

* `system_security_ssh_macs` (string)

  * MAC algorithms configuration.

* `system_security_ssh_kex_algorithms` (string)

  * Key exchange algorithms configuration.

* `system_security_ssh_host_key_algorithms` (string)

  * Host key algorithms configuration.

> Defaults intentionally disable weaker or legacy algorithms.

---

## Authorized / unauthorized SSH keys

This role can **add and revoke SSH public keys** automatically.

### Authorized keys

* `system_security_ssh_authorizedkeys_auto` (list)

  * Intended for **group vars**.

* `system_security_ssh_authorizedkeys_host` (list)

  * Intended for **host vars**.

* `system_security_ssh_authorizedkeys` (list)

  * Combined list used by the role:

    ```yaml
    system_security_ssh_authorizedkeys: "{{ system_security_ssh_authorizedkeys_auto + system_security_ssh_authorizedkeys_host }}"
    ```

* `system_security_ssh_authorized_keys_file` (string)

  * Controls the `AuthorizedKeysFile` path.

### Unauthorized (revoked) keys

* `system_security_ssh_unauthorizedkeys_auto` (list)

  * Intended for **group vars**.

* `system_security_ssh_unauthorizedkeys_host` (list)

  * Intended for **host vars**.

* `system_security_ssh_unauthorizedkeys` (list)

  * Combined list of keys to remove from `authorized_keys`.

---

## SFTP

* `system_security_ssh_subsystem_sftp_path` (string)

  * Path to the `sftp-server` binary.

---

## Extensions

* `system_security_ssh_extension` (string, default: `''`)

  * Allows injecting **additional raw sshd configuration** lines.

Example:

```yaml
system_security_ssh_extension: |
  Match User deploy
    AllowTcpForwarding yes
```

---

## Examples

### 1. Hardened default SSH (recommended baseline)

Minimal configuration relying on secure defaults:

```yaml
system_security_ssh_enabled: true
system_security_ssh_port: 22
system_security_ssh_password_authentication: false
system_security_ssh_pubkey_authentication: true
system_security_ssh_permit_root_login: false
```

---

### 2. Enable SSH port forwarding (VS Code Remote / tunnels)

Required for VS Code Remote, SSH tunnels, and similar tooling:

```yaml
system_security_ssh_allow_tcp_forwarding: true
system_security_ssh_allow_streamlocal_forwarding: true
```

> ⚠️ Consider limiting this to specific users using `Match` blocks via `system_security_ssh_extension`.

---

### 3. Bastion / jump host

Typical configuration for a bastion host with forwarding but no shell access extensions:

```yaml
system_security_ssh_allow_tcp_forwarding: true
system_security_ssh_gateway_ports: false
system_security_ssh_x11_forwarding: false
system_security_ssh_permit_tunnel: false
system_security_ssh_use_dns: false
```

---

### 4. Group-wide authorized SSH keys

Define shared keys at group level:

```yaml
system_security_ssh_authorizedkeys_auto:
  - "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA... user1@example"
  - "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5BBBB... user2@example"
```

---

### 5. Host-specific authorized SSH keys

Add or override keys for a single host:

```yaml
system_security_ssh_authorizedkeys_host:
  - "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5CCCC... deploy@example"
```

---

### 6. Revoke compromised or obsolete SSH keys

Remove keys from `authorized_keys` while keeping others intact:

```yaml
system_security_ssh_unauthorizedkeys_auto:
  - "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5OLDKEY... old@example"
```

---

### 7. Disable root login but allow deploy user with forwarding

```yaml
system_security_ssh_permit_root_login: false

system_security_ssh_extension: |
  Match User deploy
    AllowTcpForwarding yes
    X11Forwarding no
```

---

### 8. Custom SFTP-only setup

Useful for restricted file transfer users:

```yaml
system_security_ssh_extension: |
  Match User sftpuser
    ForceCommand internal-sftp
    AllowTcpForwarding no
    X11Forwarding no
```

---

## Notes

* Backward-compatible variables are preserved to avoid breaking existing inventories.
* Security-sensitive features (forwarding, tunnels, X11) are **disabled by default**.
* Always validate changes using `sshd -t` after applying custom extensions.
