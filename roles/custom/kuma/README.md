# custom/kuma

A bit hacky way to install [uptime kuma](https://github.com/louislam/uptime-kuma) with Matrix homeserver

## Requirements & install

**Put following in your matrix host's vars.yml file**:

```yml
custom_kuma_enabled: true
matrix_server_fqn_kuma: "kuma.{{ matrix_domain }}" # you can use anything you want here, it's just default value
matrix_nginx_proxy_proxy_kuma_hostname: "{{ matrix_server_fqn_kuma }}" # yep, duplicate, but it's required

matrix_ssl_additional_domains_to_obtain_certificates_for:
  - "{{ matrix_server_fqn_kuma }}"
```

Run `ansible-playbook play/all.yml -t setup-kuma`
