# custom/radicale

A bit hacky way to install [radicale](https://github.com/kozea/radicale) with Matrix homeserver

## Requirements & install

**Put following in your matrix host's vars.yml file**:

```yml
custom_radicale_enabled: true
matrix_server_fqn_radicale: "radicale.{{ matrix_domain }}" # you can use anything you want here, it's just default value
custom_radicale_htpasswd: "" # generate: htpasswd -nb user password

matrix_ssl_additional_domains_to_obtain_certificates_for:
  - "{{ matrix_server_fqn_radicale }}"
```

Run `ansible-playbook play/all.yml -t setup-radicale`
