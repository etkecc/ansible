# system/security/fail2ban

That role installs fail2ban and managed jail configuration 

> **NOTE**: check [defaults/main.yml](./defaults/main.yml) to see full list of config options

## Options

* `system_security_fail2ban_ignoreip` (string, default: `'127.0.0.1/8 ::1'`)

  * IPs, CIDRs, or DNS names fail2ban never bans. Set real infra hosts (VPN, control, monitoring) here via group vars; the default covers loopback only.

* `system_security_fail2ban_bantime_increment` (bool, default: `true`)

  * Escalates the ban duration for repeat offenders (DB-backed). Only extends the ban of an already-banned IP, so anything in `ignoreip` is never affected.
