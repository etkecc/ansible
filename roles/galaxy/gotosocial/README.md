# GoToSocial Ansible Role

![GoToSocial Logo](assets/sloth.png)

![Lint badge](https://woodpecker.hyteck.de/api/badges/moan0s/role-gotosocial/status.svg)

GoToSocial is a self-hosted [ActivityPub](https://activitypub.rocks/) social network server. This role helps you to set up GoToSocial:

- with everything run in [Docker](https://www.docker.com/) containers
- powered by [the official GoToSocial container image](https://hub.docker.com/r/superseriousbusiness/gotosocial/)


## Installing

To configure and install GoToSocial on your own server(s), you should use a playbook like [Mother of all self-hosting](https://github.com/mother-of-all-self-hosting/mash-playbook) or write your own.

# Configuring this role for your playbook

```
gotosocial_enabled: true
gotosocial_hostname: 'example.org'

gotosocial_db_host:

gotosocial_db_name:
gotosocial_db_user:
gotosocial_db_password:
```

## Support

- Github issues: [moan0s/role-gotosocial/issues](https://github.com/moan0s/role-gotosocial/issues)
