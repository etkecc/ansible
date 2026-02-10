# Restart Mode Comparison

This document compares the different `devture_systemd_service_manager_service_restart_mode` options based on real-world downtime benchmarks.

## Methodology

A server running 12+ Docker-based services (managed by this Ansible role via systemd) was restarted using each mode. During each restart, a [downtime benchmarker tool](../downtime-benchmarker/) monitored all services and measured per-service downtime.

The services included a reverse proxy (Traefik), a database (Postgres), a cache (Valkey), and various web applications — each exposed via HTTP or TCP endpoints.

### Benchmarker Configuration

The benchmarker was configured with a YAML targets file listing all public-facing endpoints:

```yaml
targets:
  # Reverse proxy (TCP - verifies TLS listener is up)
  - name: Traefik (HTTPS)
    type: tcp
    args:
      host: "example.com"
      port: 443

  - name: Hubsite
    type: http
    args:
      url: "https://example.com/"

  - name: Forgejo
    type: http
    args:
      url: "https://forgejo.example.com/"

  - name: Forgejo (SSH)
    type: tcp
    args:
      host: "example.com"
      port: 22

  - name: GoToSocial
    type: http
    args:
      url: "https://gotosocial.example.com/"

  - name: Headscale
    type: http
    args:
      url: "https://headscale.example.com/"

  - name: Miniflux
    type: http
    args:
      url: "https://example.com/miniflux/"

  - name: Navidrome
    type: http
    args:
      url: "https://example.com/navidrome/"

  - name: Nextcloud
    type: http
    args:
      url: "https://nextcloud.example.com/"

  - name: Paperless
    type: http
    args:
      url: "https://paperless.example.com/"

  - name: Vaultwarden
    type: http
    args:
      url: "https://vaultwarden.example.com/"

  - name: Syncthing (protocol)
    type: tcp
    args:
      host: "example.com"
      port: 22000
```

Checks were performed every 1 second with a 5 second timeout (the defaults).

## Results

### ⏱️ Overview

| Restart Mode | Runtime | Total Downtime | vs. `clean-stop-start` |
|---|---|---|---|
| 🐢 `clean-stop-start` | 128s | 640s | baseline |
| 🔄 `one-by-one` | 113s | 416s | -35% |
| 📦 `priority-batched` | 70s | 319s | -50% |
| 🚀 `all-at-once` | 55s | 248s | -61% |

### 📋 Per-Service Downtime (seconds)

| Service | `clean-stop-start` | `one-by-one` | `priority-batched` | `all-at-once` |
|---|---|---|---|---|
| Traefik (HTTPS) | 12 | 12 | 7 | 9 |
| Hubsite | 47 | 17 | 20 | 14 |
| Forgejo | 41 | 35 | 27 | 17 |
| Forgejo (SSH) | 12 | 13 | 7 | 10 |
| GoToSocial | 62 | 78 | 57 | 44 |
| Headscale | 42 | 17 | 22 | 14 |
| Miniflux | 47 | 22 | 27 | 14 |
| Navidrome | 53 | 16 | 11 | 14 |
| Nextcloud | 56 | 37 | 32 | 14 |
| Paperless | 115 | 124 | 71 | 69 |
| Vaultwarden | 88 | 44 | 38 | 22 |
| Syncthing (protocol) | 65 | 1 | - | 7 |
| **Total** | **640** | **416** | **319** | **248** |

### 🔁 Failure Window Counts

| Service | `clean-stop-start` | `one-by-one` | `priority-batched` | `all-at-once` |
|---|---|---|---|---|
| Traefik (HTTPS) | 1 | 2 | 1 | 1 |
| Hubsite | 1 | 3 | 2 | 1 |
| Forgejo | 1 | 3 | 1 | 1 |
| Forgejo (SSH) | 1 | 2 | 1 | 1 |
| GoToSocial | 1 | 2 | 1 | 1 |
| Headscale | 1 | 3 | 2 | 1 |
| Miniflux | 1 | 3 | 1 | 1 |
| Navidrome | 1 | 3 | 2 | 1 |
| Nextcloud | 1 | 3 | 1 | 1 |
| Paperless | 1 | 2 | 1 | 1 |
| Vaultwarden | 1 | 4 | 1 | 1 |
| Syncthing (protocol) | 1 | 1 | - | 1 |

## 🔍 Observations

- **`all-at-once` is the clear winner** — lowest runtime (55s) and lowest total downtime (248s), cutting downtime by 61% vs. the baseline. Every service experiences a single short outage window.

- **`priority-batched` is a solid middle ground** — 50% less downtime than `clean-stop-start`, with services restarted in dependency order.

- **`one-by-one` reduces total downtime but causes repeated flapping** — services go down multiple times (up to 4 failure windows for Vaultwarden) as their dependencies restart underneath them.

- **`clean-stop-start` has the most downtime** because it stops everything first, then starts — maximizing the window where services are unavailable.

- **Paperless and GoToSocial are the slowest to recover** across all modes — likely due to heavy startup initialization. They dominate the total downtime in every mode.

- **Traefik and Forgejo (SSH) recover quickly** (~7-12s) regardless of mode — these are lightweight processes with fast startup.
