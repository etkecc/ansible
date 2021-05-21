# custom/miniflux

A bit hacky way to install [Miniflux](https://miniflux.app) with Matrix homeserver

## Requirements & install

1. Put following in your matrix host's vars.yml file:

```yml
custom_miniflux_enabled: true
matrix_server_fqn_miniflux: "miniflux.{{ matrix_domain }}" # you can use anything you want here, it's just default value
matrix_nginx_proxy_proxy_miniflux_hostname: "{{ matrix_server_fqn_miniflux }}" # yep, duplicate, but it's required
custom_miniflux_database_password: "Generate strong password with `pwgen -s 64 1`"

matrix_ssl_additional_domains_to_obtain_certificates_for:
  - "{{ matrix_server_fqn_miniflux }}"
```

2. Create a database `miniflux` and user `miniflux` with superuser privileges over that database and password from vars.yml:

```sql
CREATE USER miniflux WITH PASSWORD 'myPassword';
CREATE DATABASE miniflux;
GRANT ALL PRIVILEGES ON DATABASE miniflux to miniflux;
```

3. Run `ansible-playbook play/matrix.yml -t setup-all,start`
4. Create a miniflux user with following command `docker exec -it custom-miniflux /usr/bin/miniflux -create-admin` (run it on matrix server's host)
