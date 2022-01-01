# matrix/client-cinny

A bit hacky way to install [cinny](https://github.com/ajbura/cinny) client with Matrix homeserver

## Requirements & install

**Put following in your matrix host's vars.yml file**:

```yml
matrix_client_cinny_enabled: true
matrix_server_fqn_cinny: "cinny.{{ matrix_domain }}" # you can use anything you want here, it's just default value
matrix_nginx_proxy_proxy_cinny_hostname: "{{ matrix_server_fqn_cinny }}" # yep, duplicate, but it's required

matrix_ssl_additional_domains_to_obtain_certificates_for:
  - "{{ matrix_server_fqn_cinny }}"
```

Run `ansible-playbook play/all.yml -t setup-client-cinny`
