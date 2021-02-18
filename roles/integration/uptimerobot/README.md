# integration/uptimerobot

[UptimeRobot.com](https://uptimerobot.com) is a website monitoring and status page provider.
You can use this role to automatically create and configure monitorings for all of your Matrix Homeserver's services
(including bridges and some custom services).

> **NOTE**: run this role one-time. Because of UptimeRobot API, each time you run this role, resources will be created
> in UptimeRobot, there is no usable way to properly check the state of each resource in ansible.

## Requirements

> **NOTE**: by default, pre-configured monitorings use [matrix/nginx-proxy-health](/roles/matrix/nginx-proxy-health) health page,
> but you may set and configure anything you want.
> Next documentation steps & params assumes that you use [matrix/nginx-proxy-health](/roles/matrix/nginx-proxy-health).

1. Register an account on [UptimeRobot.com](https://uptimerobot.com)
2. Put following in your matrix host's vars.yml file:

```yml
# enable the role
integration_uptimerobot_enabled: true
# UptimeRobot requires API key
integration_uptimerobot_api_key: "Your UptimeRobot MAIN API key"
# Create public status page, example: https://status.uptimerobot.com
integration_uptimerobot_statuspage_enabled: true
```

3. _(optional)_ configure custom subdomain for status page (see below)

That's enough for basic setup, those configs will configure monitoring of following components:
synapse, postgres, coturn, mailer, nginx, client-element, website (base domain).

All other components should be enabled manually, here is example list with pre-configured bridges:

```yaml
integration_uptimerobot_monitors_custom:
  - enabled: true
    options:
      friendly_name: 'Bridge: email'
      keyword_type: 2
      keyword_value: "matrix-email2matrix.service                                                                           loaded    active     running"
      status: 1
      type: 2
      url: "{{ integration_uptimerobot_healthurl }}"
  - enabled: true
    options:
      friendly_name: Webhooks
      keyword_type: 2
      keyword_value: "matrix-appservice-webhooks.service                                                                    loaded    active     running"
      status: 1
      type: 2
      url: "{{ integration_uptimerobot_healthurl }}"
  - enabled: true
    options:
      friendly_name: 'Bridge: discord'
      keyword_type: 2
      keyword_value: "matrix-mx-puppet-discord.service                                                                      loaded    active     running"
      status: 1
      type: 2
      url: "{{ integration_uptimerobot_healthurl }}"
  - enabled: true
    options:
      friendly_name: 'Bridge: slack'
      keyword_type: 2
      keyword_value: "matrix-mx-puppet-slack.service                                                                        loaded    active     running"
      status: 1
      type: 2
      url: "{{ integration_uptimerobot_healthurl }}"
  - enabled: true
    options:
      friendly_name: 'Bridge: telegram'
      keyword_type: 2
      keyword_value: "matrix-mautrix-telegram.service                                                                       loaded    active     running"
      status: 1
      type: 2
      url: "{{ integration_uptimerobot_healthurl }}"
  - enabled: true
    options:
      friendly_name: 'Bridge: whatsapp'
      keyword_type: 2
      keyword_value: "matrix-mautrix-whatsapp.service                                                                       loaded    active     running"
      status: 1
      type: 2
      url: "{{ integration_uptimerobot_healthurl }}"
```

## Configuration

> **NOTE**: check [defaults/main.yml](./defaults/main.yml) to see full list of config options

### integration_uptimerobot_enabled

Enable the role, default: `false`

### integration_uptimerobot_api_key

UptimeRobot main API key

### integration_uptimerobot_domain

Base domain name (host, without schema or path) of your matrix homeserver, default: `{{ matrix_domain }}`

### integration_uptimerobot_healthurl

URL of the matrix/nginx-proxy-health report / status page, default: `"https://{{ integration_uptimerobot_domain }}/{{ matrix_nginx_proxy_health_file }}"`

### integration_uptimerobot_recreate

allow to update (REMOVE and create) of existing monitors, default: `false`

### integration_uptimerobot_statuspage

Status page configuration

### integration_uptimerobot_statuspage_enabled

Enable status page, default: `false`

### integration_uptimerobot_statuspage_options

Configuration options of status page

#### friendly_name

Status page title, default: `"{{ integration_uptimerobot_domain }} Status"`

#### type

Satus page type, default: `1`

#### monitors

List of included monitors, default: `0` - include all

#### custom_domain

Custom domain for your status page, default: "status.{{ integration_uptimerobot_domain }}"

If you want to use it, you must add CNAME record, pointing to `stats.uptimerobot.com`, example:

```
status.yourwebsite.com.		1799	IN	CNAME	stats.uptimerobot.com.
```


### integration_uptimerobot_monitors_custom

List of your own monitor configs, scroll up for examples.
