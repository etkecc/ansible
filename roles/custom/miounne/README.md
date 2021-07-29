# custom/miounne

A bit hacky way to install [Miounne](https://gitlab.com/etke.cc/miounne) with Matrix homeserver

## Requirements & install

1. **Put following in your matrix host's vars.yml file**:

```yml
custom_miounne_enabled: true
custom_miounne_database_password: 'STRONG_SECURE_PASSWORD'
matrix_server_fqn_miounne: "miounne.{{ matrix_domain }}" # you can use anything you want here, it's just default value
matrix_nginx_proxy_proxy_miounne_hostname: "{{ matrix_server_fqn_miounne }}" # yep, duplicate, but it's required

matrix_ssl_additional_domains_to_obtain_certificates_for:
  - "{{ matrix_server_fqn_miounne }}"
```

2. Create database:

```sql
CREATE USER custom_miounne WITH PASSWORD 'STRONG_SECURE_PASSWORD';
CREATE DATABASE custom_miounne;
GRANT ALL PRIVILEGES ON DATABASE custom_miounne to custom_miounne;
```

Run `ansible-playbook play/all.yml -t setup-miounne,start-miounne`
