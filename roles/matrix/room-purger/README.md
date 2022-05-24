# matrix/room-purger

That role installs [room-purger](https://gitlab.com/etke.cc/room-purger)

## Requirements

Put following in your matrix host's vars.yml file:

```yml
matrix_room_purger_enabled: yes
matrix_room_purger_login: homeserver_admin_login
matrix_room_purger_password: homeserver_admin_password
matrix_room_purger_search: Search Criteria
```

It runs every night (between 4am and 6am) and purges all rooms, based on search criteria
