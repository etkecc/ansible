# custom/miounne

A bit hacky way to install [Miounne](https://gitlab.com/etke.cc/miounne) with Matrix homeserver

## Requirements & install

1. **Put following in your matrix host's vars.yml file**:

```yml
custom_miounne_enabled: true
matrix_server_fqn_miounne: "miounne.{{ matrix_domain }}" # you can use anything you want here, it's just default value

matrix_ssl_additional_domains_to_obtain_certificates_for:
  - "{{ matrix_server_fqn_miounne }}"
```

2. Run `ansible-playbook play/all.yml -t setup-miounne,start-miounne`
