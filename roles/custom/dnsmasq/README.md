# custom/dnsmasq

Role to install dnsmasq on your matrix server.

## Requirements & install

**Put following in your matrix host's vars.yml file**:

```yml
custom_dnsmasq_enabled: true
```

After that your server will serve DNS recursive resolver on `53` (default) port
