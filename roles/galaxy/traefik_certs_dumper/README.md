# Traefik certs dumper Ansible role

This is an [Ansible](https://www.ansible.com/) role which installs [traefik-certs-dumper](https://github.com/ldez/traefik-certs-dumper) - a tool which dumps [ACME](https://en.wikipedia.org/wiki/Automatic_Certificate_Management_Environment) certificates (like [Let's Encrypt](https://letsencrypt.org/)) from [Traefik](https://traefik.io/)'s `acme.json` file into some directory. The playbook installs the tool to run as a [Docker](https://www.docker.com/) container wrapped in a systemd service.

This role *implicitly* depends on [`com.devture.ansible.role.systemd_docker_base`](https://github.com/devture/com.devture.ansible.role.systemd_docker_base).

This role is related to the [com.devture.ansible.role.traefik](https://github.com/devture/com.devture.ansible.role.traefik) role and integrates nicely with it, but using them both together is **not** a requirement.

## Usage

Example playbook:

```yaml
- hosts: servers
  roles:
    - role: galaxy/com.devture.ansible.role.systemd_docker_base

    # You can also install Traefik in another way and avoid using this role.
    - role: galaxy/com.devture.ansible.role.traefik

    - role: galaxy/com.devture.ansible.role.traefik_certs_dumper

    - role: another_role
```

Example playbook configuration (`group_vars/servers` or other):

```yaml
# Traefik role (com.devture.ansible.role.traefik) configuration here, if you're using it.
# If not, you can adjust the configuration below to make it work with your own Traefik server.

devture_traefik_certs_dumper_uid: "{{ my_uid }}"
devture_traefik_certs_dumper_gid: "{{ my_gid }}"

devture_traefik_certs_dumper_ssl_dir_path: "{{ devture_traefik_ssl_dir_path }}"
```

### systemd

#### devture-traefik-certs-dumper.service

You can then start the `devture-traefik-certs-dumper.service` systemd service, which watches for a certificate file (`acme.json`, but configurable via `devture_traefik_certs_dumper_ssl_acme_file_name`) in the SSL certificates directory (`devture_traefik_certs_dumper_ssl_dir_path`).

When a certificate file appears or whenever it changes in the future, all of its certificates are:

- dumped using [traefik-certs-dumper](https://github.com/ldez/traefik-certs-dumper) to `/devture-traefik-certs-dumper/dumped-certificates` (configurable via `devture_traefik_certs_dumper_dumped_certificates_dir_path`)
- re-chowned, so that they're owned by `devture_traefik_certs_dumper_dumped_certificates_dir_owner` / `devture_traefik_certs_dumper_dumped_certificates_dir_owner` (defaulting to `devture_traefik_certs_dumper_uid` and `devture_traefik_certs_dumper_gid`, respectively)

The directory tree would look like this:

```
/devture-traefik-certs-dumper/dumped-certificates/
├── example.com
│   ├── certificate.crt
│   └── privatekey.key
├── another.example.com
│   ├── certificate.crt
│   └── privatekey.key
└── private
    └── letsencrypt.key
```

#### devture-traefik-certs-dumper-wait-for-domain@.service

To help you launch other services which depend on these dumped certificate files, this role also provides an [instantiated systemd service](https://www.freedesktop.org/software/systemd/man/systemd.service.html#Service%20Templates) called `devture-traefik-certs-dumper-wait-for-domain@.service`.

You can adjust your systemd `.service` file definitions to add `Requires` and `After` clauses like this:

```
Requires=devture-traefik-certs-dumper-wait-for-domain@DOMAIN_NAME.service
After=devture-traefik-certs-dumper-wait-for-domain@DOMAIN_NAME.service
```

Then, upon launching your service:

- the "waiter" service will be started as a dependency

- it will wait for certificates for the specified domain (`DOMAIN_NAME`) to become available (e.g. `/devture-traefik-certs-dumper/dumped-certificates/DOMAIN_NAME/certificate.crt` and `/devture-traefik-certs-dumper/dumped-certificates/DOMAIN_NAME/privatekey.key`)

By default, the "waiter" service waits for 30 seconds (configurable via `devture_traefik_certs_dumper_waiter_max_iterations`) before giving up and aborting execution of your service.
