<!--
SPDX-FileCopyrightText: 2020 - 2024 MDAD project contributors
SPDX-FileCopyrightText: 2020 - 2024 Slavi Pantaleev
SPDX-FileCopyrightText: 2020 Aaron Raimist
SPDX-FileCopyrightText: 2020 Chris van Dijk
SPDX-FileCopyrightText: 2020 Dominik Zajac
SPDX-FileCopyrightText: 2020 Mickaël Cornière
SPDX-FileCopyrightText: 2022 François Darveau
SPDX-FileCopyrightText: 2022 Julian Foad
SPDX-FileCopyrightText: 2022 Warren Bailey
SPDX-FileCopyrightText: 2023 Antonis Christofides
SPDX-FileCopyrightText: 2023 Felix Stupp
SPDX-FileCopyrightText: 2023 Pierre 'McFly' Marty
SPDX-FileCopyrightText: 2024 - 2025 Suguru Hirahara
SPDX-FileCopyrightText: 2025 Nicola Murino

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# Setting up traefik-certs-dumper

This is an [Ansible](https://www.ansible.com/) role which installs [traefik-certs-dumper](https://github.com/ldez/traefik-certs-dumper) to run as a [Docker](https://www.docker.com/) container wrapped in a systemd service.

traefik-certs-dumper is a tool which dumps [ACME](https://en.wikipedia.org/wiki/Automatic_Certificate_Management_Environment) certificates (like [Let's Encrypt](https://letsencrypt.org/)) from [Traefik](https://traefik.io/)'s `acme.json` file into some directory.

See the project's [documentation](https://github.com/ldez/traefik-certs-dumper/blob/main/readme.md) to learn what traefik-certs-dumper does and why it might be useful to you.

## Adjusting the playbook configuration

To enable traefik-certs-dumper with this role, add the following configuration to your `vars.yml` file.

**Note**: the path should be something like `inventory/host_vars/mash.example.com/vars.yml` if you use the [MASH Ansible playbook](https://github.com/mother-of-all-self-hosting/mash-playbook).

```yaml
########################################################################
#                                                                      #
# traefik_certs_dumper                                                 #
#                                                                      #
########################################################################

traefik_certs_dumper_enabled: true

traefik_certs_dumper_ssl_path: "{{ traefik_ssl_dir_path }}"

########################################################################
#                                                                      #
# /traefik_certs_dumper                                                #
#                                                                      #
########################################################################
```

## Installing

After configuring the playbook, run the installation command of your playbook as below:

```sh
ansible-playbook -i inventory/hosts setup.yml --tags=setup-all,start
```

If you use the MASH playbook, the shortcut commands with the [`just` program](https://github.com/mother-of-all-self-hosting/mash-playbook/blob/main/docs/just.md) are also available: `just install-all` or `just setup-all`

## Usage

### traefik-certs-dumper.service

After running the command for installation, you can start the `traefik-certs-dumper.service` systemd service, which watches for a certificate file (`acme.json`, but configurable via `traefik_certs_dumper_ssl_acme_file_name`) in the SSL certificates directory (`traefik_certs_dumper_ssl_path`).

When a certificate file appears or whenever it changes in the future, all of its certificates are:

- dumped using [traefik-certs-dumper](https://github.com/ldez/traefik-certs-dumper) to `/traefik-certs-dumper/dumped-certificates` (configurable via `traefik_certs_dumper_dumped_certificates_path`)
- re-chowned, so that they're owned by `traefik_certs_dumper_dumped_certificates_dir_owner` / `traefik_certs_dumper_dumped_certificates_dir_owner` (defaulting to `traefik_certs_dumper_uid` and `traefik_certs_dumper_gid`, respectively)

The directory tree would look like this:

```txt
/traefik-certs-dumper/dumped-certificates/
├── example.com
│   ├── certificate.crt
│   └── privatekey.key
├── another.example.com
│   ├── certificate.crt
│   └── privatekey.key
└── private
    └── letsencrypt.key
```

### traefik-certs-dumper-wait-for-domain@.service

To help you launch other services which depend on these dumped certificate files, this role also provides an [instantiated systemd service](https://www.freedesktop.org/software/systemd/man/systemd.service.html#Service%20Templates) called `traefik-certs-dumper-wait-for-domain@.service`.

You can adjust your systemd `.service` file definitions to add `Requires` and `After` clauses like this:

```txt
Requires=traefik-certs-dumper-wait-for-domain@DOMAIN_NAME.service
After=traefik-certs-dumper-wait-for-domain@DOMAIN_NAME.service
```

Then, upon launching your service:

- the "waiter" service will be started as a dependency

- it will wait for certificates for the specified domain (`DOMAIN_NAME`) to become available (e.g. `/traefik-certs-dumper/dumped-certificates/DOMAIN_NAME/certificate.crt` and `/traefik-certs-dumper/dumped-certificates/DOMAIN_NAME/privatekey.key`)

By default, the "waiter" service waits for 30 seconds (configurable via `traefik_certs_dumper_waiter_max_iterations`) before giving up and aborting execution of your service.

## Troubleshooting

### Check the service's logs

You can find the logs in [systemd-journald](https://www.freedesktop.org/software/systemd/man/systemd-journald.service.html) by logging in to the server with SSH and running `journalctl -fu traefik-certs-dumper` (or how you/your playbook named the service, e.g. `mash-traefik-certs-dumper`).
