# Downtime Benchmarker

A CLI tool that measures service downtime during maintenance windows (e.g., rolling restarts). It monitors a list of HTTP and TCP endpoints at a configurable interval, detects failures, and on `Ctrl+C` prints a per-target and total downtime report.

## Building

```sh
just build

# or for an optimized binary
just release
```

## Usage

```sh
just run -- --target-urls targets.yml
```

Or directly:

```sh
cargo run -- --target-urls targets.yml [--check-interval <seconds>] [--timeout <seconds>]
```

### CLI Options

| Option | Default | Description |
|---|---|---|
| `--target-urls` | (required) | Path to the YAML targets file |
| `--check-interval` | `1` | Seconds between checks |
| `--timeout` | `5` | Per-check timeout in seconds |

## Targets File Format

Each target has a `name`, a `type` (`http` or `tcp`), and type-specific `args`. See [targets.yml.example](targets.yml.example) for a full example.

```yaml
targets:
  - name: My Website
    type: http
    args:
      url: "https://example.com/"

  - name: Database
    type: tcp
    args:
      host: "192.168.1.10"
      port: 5432
```

### Check Types

| Type | Args | Healthy when |
|---|---|---|
| `http` | `url` | HTTP GET returns 2xx or 3xx |
| `tcp` | `host`, `port` | TCP connection succeeds |

IPv6 addresses are supported for TCP checks (e.g., `host: "2001:db8::1"`).

Unknown check types or unexpected args are rejected at startup with a descriptive error.

## How It Works

1. Loads and validates the targets file
2. Runs an initial health check — if any target is down, exits with an error
3. Enters the monitoring loop, checking all targets concurrently every `--check-interval` seconds
4. Tracks failure windows per target (when a target transitions from healthy to failing, and back)
5. On `Ctrl+C`, prints a report sorted by time of first failure

### Example Report

```
📊 Downtime Benchmarking Results
═══════════════════════════════

🔴 Failures started at: 14:32:49

📋 Details (sorted by time of first failure):

  🌐 My Website
     Total downtime: 32s | 2 failure(s)
     ├── 20s @ 14:32:49
     └── 12s @ 14:35:00

  🔌 Database
     Total downtime: 1s | 1 failure(s)
     └── 1  s @ 14:33:02

───────────────────────────────
⏱️  Total downtime: 33s
```

## Pre-commit Hooks

```sh
just prek-install-git-pre-commit-hook
```

This installs a git pre-commit hook (via [mise](https://mise.jdx.dev/) + [prek](https://github.com/prek-sh/prek)) that runs formatting and linting checks before each commit.
