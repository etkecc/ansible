# custom/languagetool

A bit hacky way to install [LanguageTool server](https://languagetool.org) with Matrix homeserver

## Requirements & install

**Put following in your matrix host's vars.yml file**:

```yml
custom_languagetool_enabled: true
custom_languagetool_ngrams_enabled: true #WARNING: requires A LOT of storage (zip is > 8gb, unpacked - even more!)
matrix_server_fqn_languagetool: "languagetool.{{ matrix_domain }}" # you can use anything you want here, it's just default value

matrix_ssl_additional_domains_to_obtain_certificates_for:
  - "{{ matrix_server_fqn_languagetool }}"
```

Run `ansible-playbook play/all.yml -t setup-languagetool,start-languagetool`
