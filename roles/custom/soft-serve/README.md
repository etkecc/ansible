# custom/soft-serve

Install [soft-serve](https://github.com/charmbracelet/soft-serve) with Matrix homeserver

## Requirements & install

**Put following in your matrix host's vars.yml file**:

```yml
custom_softserve_enabled: true
custom_softserve_host: "matrix.{{ matrix_domain }}"
custom_softserve_pubkey: "your public key"
```

Run `ansible-playbook play/all.yml -t setup-softserve`
