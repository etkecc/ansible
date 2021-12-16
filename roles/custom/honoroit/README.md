# custom/honoroit

A bit hacky way to install [honoroit](https://gitlab.com/etke.cc/honoroit) with Matrix homeserver

## Requirements & install

1. **Put following in your matrix host's vars.yml file**:

```yml
custom_honoroit_enabled: true
custom_honoroit_login: honoroit
custom_honoroit_password: securePassword
custom_honoroit_roomid: "!backofficeRoomID:your.server"
```

2. Run `ansible-playbook play/all.yml -t setup-honoroit,start-honoroit`
