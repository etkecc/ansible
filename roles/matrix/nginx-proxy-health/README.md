# matrix/nginx-proxy-health

Publish simple healthcheck/status page of your matrix services,

example:

```html
<pre>
-> matrix-mx-puppet-discord.service loaded active running Matrix Mx Puppet Discord bridge
-> matrix-mautrix-whatsapp.service loaded active running Matrix Mautrix Whatsapp bridge
-> matrix-nginx-proxy.service loaded active running Matrix nginx-proxy server matrix-ssl-nginx-proxy-reload.timer loaded active waiting Reloads matrix-nginx-proxy periodically so that new SSL certificates can kick in
-> matrix-mx-puppet-slack.service loaded active running Matrix Mx Puppet Slack bridge
-> matrix-mailer.service loaded active running Matrix mailer
-> matrix-client-element.service loaded active running Matrix Element server
-> matrix-ssl-nginx-proxy-reload.timer loaded active waiting Reloads matrix-nginx-proxy periodically so that new SSL certificates can kick in
-> matrix-coturn.service loaded active running Matrix Coturn server matrix-coturn-reload.timer loaded active waiting Reloads matrix-coturn periodically so that new SSL certificates can kick in
-> matrix-coturn-reload.timer loaded active waiting Reloads matrix-coturn periodically so that new SSL certificates can kick in
-> matrix-ssl-lets-encrypt-certificates-renew.timer loaded active waiting Renews Let's Encrypt SSL certificates periodically
-> matrix-mautrix-telegram.service loaded active running Matrix Mautrix Telegram bridge
-> matrix-postgres.service loaded active running Matrix Postgres server
-> matrix-ssl-lets-encrypt-certificates-renew.timer loaded active waiting Renews Let's Encrypt SSL certificates periodically
-> matrix-synapse-admin.service loaded active running matrix-synapse-admin matrix-synapse.service loaded active running Synapse server
-> matrix-coturn-reload.timer loaded active waiting Reloads matrix-coturn periodically so that new SSL certificates can kick in
-> matrix-ssl-nginx-proxy-reload.timer loaded active waiting Reloads matrix-nginx-proxy periodically so that new SSL certificates can kick in
-> matrix-appservice-webhooks.service loaded active running Matrix Appservice webhooks bridge
</pre>
```

Usecase - "keyword exists" monitoring check

## Requirements

1. Put following in your matrix host's vars.yml file:

```yml
matrix_nginx_proxy_health_enabled: true
```

## Configuration

> **NOTE**: check [defaults/main.yml](./defaults/main.yml) to see full list of config options

### matrix_nginx_proxy_health_enabled

Enable health report, default: `false`

### matrix_nginx_proxy_health_file

Filename for status report, default: `health.html`

### matrix_nginx_proxy_health_timer

How often report file should be updated (minutes), default: `1` minute
