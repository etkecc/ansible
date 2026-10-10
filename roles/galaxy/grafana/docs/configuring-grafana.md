<!--
SPDX-FileCopyrightText: 2020 Chris van Dijk
SPDX-FileCopyrightText: 2020 Dominik Zajac
SPDX-FileCopyrightText: 2020 Mickaël Cornière
SPDX-FileCopyrightText: 2020, 2021 Aaron Raimist
SPDX-FileCopyrightText: 2020-2024 MDAD project contributors
SPDX-FileCopyrightText: 2020-2024 Slavi Pantaleev
SPDX-FileCopyrightText: 2021 Kim Brose
SPDX-FileCopyrightText: 2021 Luca Di Carlo
SPDX-FileCopyrightText: 2022 François Darveau
SPDX-FileCopyrightText: 2022 Julian Foad
SPDX-FileCopyrightText: 2022 Olivér Falvai
SPDX-FileCopyrightText: 2022 Warren Bailey
SPDX-FileCopyrightText: 2023 Antonis Christofides
SPDX-FileCopyrightText: 2023 Borislav Pantaleev
SPDX-FileCopyrightText: 2023 Felix Stupp
SPDX-FileCopyrightText: 2023 Julian-Samuel Gebühr
SPDX-FileCopyrightText: 2023 Michael Hollister
SPDX-FileCopyrightText: 2023 Pierre 'McFly' Marty
SPDX-FileCopyrightText: 2024 Igor Goldenberg
SPDX-FileCopyrightText: 2024 Thomas Miceli
SPDX-FileCopyrightText: 2024-2026 Suguru Hirahara
SPDX-FileCopyrightText: 2025 MASH project contributors

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# Setting up Grafana

This is an [Ansible](https://www.ansible.com/) role which installs [Grafana](https://grafana.com/) to run as a [Docker](https://www.docker.com/) container wrapped in a systemd service.

Grafana is a web-based tool for visualizing your [Prometheus](https://prometheus.io/) metrics (time-series).

See the project's [documentation](https://grafana.com/docs/) to learn what Grafana does and why it might be useful to you.

> [!WARNING]
> Metrics and graphs contain a lot of information, and anyone who has access to them can make an educated guess about your server usage patterns. This especially applies to small personal/family scale homeservers, where the number of samples is fairly limited. Analyzing the metrics over time, one might be able to figure out your life cycle, such as when you wake up, go to bed, etc. Before enabling (anonymous) access, you should carefully evaluate the risk, and if you do enable it, it is highly recommended to change your Grafana password from the default one.

## Adjusting the playbook configuration

To enable Grafana with this role, add the following configuration to your `vars.yml` file.

**Note**: the path should be something like `inventory/host_vars/mash.example.com/vars.yml` if you use the [MASH Ansible playbook](https://github.com/mother-of-all-self-hosting/mash-playbook).

```yaml
########################################################################
#                                                                      #
# grafana                                                              #
#                                                                      #
########################################################################

grafana_enabled: true

########################################################################
#                                                                      #
# /grafana                                                             #
#                                                                      #
########################################################################
```

### Set the hostname

To enable Grafana you need to set the hostname as well. To do so, add the following configuration to your `vars.yml` file. Make sure to replace `example.com` with your own value.

```yaml
grafana_hostname: "example.com"
```

After adjusting the hostname, make sure to adjust your DNS records to point the domain to your server.

### Setting administrator's account details (optional)

By default Grafana creates a user with `admin` as the username and password. You are asked to change the credentials on first login. If this is insecure for you, you can change them beforehand by adding the following configuration to your `vars.yml` file:

```yaml
grafana_default_admin_user: ADMIN_USERNAME_HERE
grafana_default_admin_password: ADMIN_PASSWORD_HERE
```

Generating a strong password (e.g. `pwgen -s 64 1`) is recommended for `grafana_default_admin_password`.

>[!NOTE]
> Subsequent changes to them will not affect the existing user.

### Allowing anonymous access (optional)

By default viewing graphs requires you to log in to the instance. If you want to publicly share graphs (e.g. when asking for help in [`#synapse:matrix.org`](https://matrix.to/#/#synapse:matrix.org) about the Matrix homeserver configuration), you'll want to allow anonymous access by adding the following configuration to your `vars.yml` file:

```yaml
grafana_anonymous_access: true
```

### Configuring a SMTP mailer (optional)

You can configure a SMTP mailer to enable email functions such as password recovery.

To configure it, add the following configuration to your `vars.yml` file as below (adapt to your needs):

```yaml
grafana_mailer_enabled: true

# Specify SMTP server hostname
grafana_config_smtp_host: ""

# Specify SMTP server port number
grafana_config_smtp_port: 587

# Specify SMTP server username
grafana_config_smtp_user: ""

# Specify SMTP server password
grafana_config_smtp_password: ""

# Specify the email address that emails will be sent from
grafana_config_smtp_from_address: ""
```

Refer to [this page](https://grafana.com/docs/grafana/latest/alerting/configure-notifications/manage-contact-points/integrations/configure-email/) on the official documentation for details.

>[!WARNING]
> Without setting an authentication method such as DKIM, SPF, and DMARC for your hostname, emails are most likely to be quarantined as spam at recipient's mail servers. The worst scenario is that your server's IP address or hostname will be included in the spam list such as the one managed by [Spamhaus](https://www.spamhaus.org/). If you have set up a mail server with the [MASH project's exim-relay Ansible role](https://github.com/mother-of-all-self-hosting/ansible-role-exim-relay), you can enable DKIM signing with it. Refer [its documentation](https://github.com/mother-of-all-self-hosting/ansible-role-exim-relay/blob/main/docs/configuring-exim-relay.md#enable-dkim-support-optional) for details.

### File provisioning

The fully configured Grafana instance is a system of multiple components, such as dashboards, data sources, notification points, other resources, and so on. All of these things can be configured via the UI, but many of them can also be configured directly via "File provisioning".

To see all components with file provisioning support, refer to [`defaults/main.yml`](../defaults/main.yml) and search for variables starting with `grafana_provisioning_`.

>[!NOTE]
> If you're enabling multiple of one component, you need to "merge" the configurations. Do not define `grafana_provisioning_datasources_datasources` twice, but combine them.

#### Datasources

For Grafana to create graphs, charts, and alerts it needs to pull data from a metrics (time-series) database like Prometheus. This can be set up with the `grafana_provisioning_datasources_datasources` variable.

By default Grafana will automatically delete previously provisioned data sources when they’re removed from `grafana_provisioning_datasources_datasources` via the `grafana_provisioning_datasources_prune` variable. If you want to manually delete provisioned datasources instead, add the following configuration:

```yaml
grafana_provisioning_datasources_prune: false
grafana_provisioning_datasources_deleteDatasources:
  - name: Prometheus
    orgId: 1

  - name: Loki
    orgId: 1
```

#### Integrating with a local Prometheus instance

If Prometheus runs on the same server and is connected to the Grafana's container network, you can hook Grafana to it with the following additional configuration:

>[!NOTE]
> The configuration below presupposes that Prometheus is set up with the [ansible-role-prometheus](https://github.com/mother-of-all-self-hosting/ansible-role-prometheus) Ansible role on the MASH Ansible playbook. Adapt to your needs if it is set up otherwise.

```yaml
grafana_provisioning_datasources_datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: "http://{{ prometheus_identifier }}:9090"
    jsonData:
      timeInterval: "{{ prometheus_config_global_scrape_interval }}"
    # Enable below if connecting to a remote instance that uses Basic Auth.
    # basicAuth: true
    # basicAuthUser: loki
    # secureJsonData:
    #   basicAuthPassword: ""
```

For connecting to a remote Prometheus instance, you may need to adjust this configuration.

#### Integrating with a local Loki instance

>[!NOTE]
> The configuration below presupposes that Grafana Loki is set up with the [ansible-role-loki](https://github.com/mother-of-all-self-hosting/ansible-role-loki) Ansible role on the MASH Ansible playbook. Adapt to your needs if it is set up otherwise.

If [Grafana Loki](https://grafana.com/docs/loki/latest/) runs on the same server, you can hook Grafana to it over the container network with the following additional configuration:

```yaml
grafana_provisioning_datasources_datasources:
  - name: Loki (your-tenant-id)
    type: loki
    access: proxy
    url: "{{ loki_scheme }}://{{ loki_identifier }}:{{ loki_server_http_listen_port }}"
    # Enable below and also (basicAuthPassword) if connecting to a remote instance that uses Basic Auth.
    # basicAuth: true
    # basicAuthUser: loki
    jsonData:
      httpHeaderName1: X-Scope-OrgID
    secureJsonData:
      httpHeaderValue1: "your-tenant-id"
      # basicAuthPassword: ""
```

For connecting to a remote Loki instance, you may need to adjust this configuration.

If [Promtail](https://grafana.com/docs/loki/latest/send-data/promtail/) runs on the same server as Loki, by default it is configured to send `mash` as the tenant ID.

#### Alerts

With alerts you can receive notifications when specific conditions regarding your data are met. Since there is no "prune" option (like datasources) you need to add alerts to `grafana_provisioning_alerts_deleteRules` when you want it removed.

The example below is truncated. Refer to the [official example](https://github.com/grafana/provisioning-alerting-examples/blob/main/config-files/grafana/provisioning/alerting/alert_rules.yaml) for a full example. As you can see in the official example, these YAML alerts are not very human readable. It is recommended you create your alert in the UI and then select the "Export rules" option to create the proper values.

```yaml
grafana_provisioning_alerts_groups:
  - orgId: 1
    name: my_rule_group
    folder: my_first_folder
    interval: 60s
    rules:
      - uid: my_id_1

grafana_provisioning_alerts_deleteRules:
  - orgId: 1
    uid: my_id_1
```

#### Contact points

To specify the place where a firing alert should be routed to (Slack, Discord, Webhook URL, etc.) you need to configure a contact point. The prune support does not exist for contact points either, so you need to add the alert to `grafana_provisioning_contact_points_contactPoints` when you want it removed.

```yaml
grafana_provisioning_contact_points_contactPoints:
  - orgId: 1
    name: Matrix
    receivers:
      - uid: first_uid
        type: webhook
        disableResolveMessage: false
        settings:
          url: "https://matrix.example.com/_matrix/maubot/plugin/bot.maubot.alertbot/webhook/!roomid"

grafana_provisioning_contact_points_deleteContactPoints:
  - orgId: 1
    uid: first_uid
```

### Integrating with Prometheus Node Exporter

>[!NOTE]
> The configuration below presupposes that Prometheus Node Exporter is set up with the [ansible-role-prometheus-node-exporter](https://github.com/mother-of-all-self-hosting/ansible-role-prometheus-node-exporter) Ansible role on the MASH Ansible playbook. Adapt to your needs if it is set up otherwise.

If you've installed [Prometheus Node Exporter](https://github.com/prometheus/node_exporter) on any host (target) scraped by Prometheus, you may wish to install a dashboard for it.

The Prometheus Node Exporter role exposes a list of URLs containing dashboards (JSON files) in its `prometheus_node_exporter_dashboard_urls` variable.

You can add this additional configuration to make the Grafana service pull these dashboards:

```yaml
grafana_dashboard_download_urls: |
  {{
    prometheus_node_exporter_dashboard_urls
  }}
```

### Configuring Single-Sign-On

Grafana supports Single-Sign-On (SSO) via OAuth. To make use of this you'll need an Identity Provider (IdP) like [authentik](https://goauthentik.io/), [Authelia](https://www.authelia.com/), [Keycloak](https://www.keycloak.org/), or [Pocket ID](https://pocket-id.org).

Below are examples for Grafana configuration.

#### authentik

- Create a new OAuth provider in authentik called `grafana`
- Create an application also named `grafana` in authentik using this provider
- Adjust `authentik.example.com`

```yaml
# To make Grafana honor the expiration time of JWT tokens, enable this experimental feature below.
# grafana_feature_toggles_enable: accessTokenExpirationCheck

grafana_environment_variables_additional_variables: |
  GF_AUTH_GENERIC_OAUTH_ENABLED=true
  GF_AUTH_GENERIC_OAUTH_NAME=authentik
  GF_AUTH_GENERIC_OAUTH_CLIENT_ID=COPIED-CLIENTID
  GF_AUTH_GENERIC_OAUTH_CLIENT_SECRET=COPIED-CLIENTSECRET
  GF_AUTH_GENERIC_OAUTH_SCOPES=openid profile email
  GF_AUTH_GENERIC_OAUTH_AUTH_URL=https://authentik.example.com/application/o/authorize/
  GF_AUTH_GENERIC_OAUTH_TOKEN_URL=https://authentik.example.com/application/o/token/
  GF_AUTH_GENERIC_OAUTH_API_URL=https://authentik.example.com/application/o/userinfo/
  GF_AUTH_SIGNOUT_REDIRECT_URL=https://authentik.example.com/application/o/grafana/end-session/
  # Optionally enable auto-login (bypasses Grafana login screen)
  #GF_AUTH_OAUTH_AUTO_LOGIN="true"
  GF_AUTH_GENERIC_OAUTH_ALLOW_ASSIGN_GRAFANA_ADMIN=true
  # Optionally map user groups to Grafana roles
  GF_AUTH_GENERIC_OAUTH_ROLE_ATTRIBUTE_PATH=contains(groups[*], 'Grafana Admins') && 'Admin' || contains(groups[*], 'Grafana Editors') && 'Editor' || 'Viewer'
```

Make sure the user you want to login as has an email address in authentik, otherwise there will be an error.

#### Authelia

>[!NOTE]
> The configuration below presupposes that Authelia is set up with the [ansible-role-authelia](https://github.com/mother-of-all-self-hosting/ansible-role-authelia) Ansible role on the MASH Ansible playbook. Adapt to your needs if it is set up otherwise.

- Come up with a client ID you'd like to use. Example: `grafana`
- Generate a shared secret for the OpenID Connect application: `pwgen -s 64 1`. This is to be used in `GF_AUTH_GENERIC_OAUTH_CLIENT_SECRET` below
- Hash the shared secret for use in Authelia's configuration (`authelia_config_identity_providers_oidc_clients`): `php -r 'echo password_hash("PASSWORD_HERE",  PASSWORD_ARGON2ID);'`. Feel free to use another language (or tool) for creating a hash as well. A few different hash algorithms are supported besides Argon2id.
- Define this `grafana` client in Authelia via `authelia_config_identity_providers_oidc_clients`. Refer to [example configuration](https://github.com/mother-of-all-self-hosting/mash-playbook/blob/main/docs/services/authelia.md#protecting-a-service-with-openid-connect) on the MASH playbook's documentation page for Authelia.

```yaml
# To make Grafana honor the expiration time of JWT tokens, enable this experimental feature below.
# grafana_feature_toggles_enable: accessTokenExpirationCheck

grafana_environment_variables_additional_variables: |
  GF_AUTH_GENERIC_OAUTH_ENABLED=true
  GF_AUTH_GENERIC_OAUTH_NAME=Authelia
  GF_AUTH_GENERIC_OAUTH_CLIENT_ID=grafana
  GF_AUTH_GENERIC_OAUTH_CLIENT_SECRET=PLAIN_TEXT_SHARED_SECRET
  GF_AUTH_GENERIC_OAUTH_SCOPES=openid profile email groups
  GF_AUTH_GENERIC_OAUTH_EMPTY_SCOPES=false
  GF_AUTH_GENERIC_OAUTH_AUTH_URL=https://authelia.example.com/api/oidc/authorization
  GF_AUTH_GENERIC_OAUTH_TOKEN_URL=https://authelia.example.com/api/oidc/token
  GF_AUTH_GENERIC_OAUTH_API_URL=https://authelia.example.com/api/oidc/userinfo
  GF_AUTH_GENERIC_OAUTH_LOGIN_ATTRIBUTE_PATH=preferred_username
  GF_AUTH_GENERIC_OAUTH_GROUPS_ATTRIBUTE_PATH=groups
  GF_AUTH_GENERIC_OAUTH_NAME_ATTRIBUTE_PATH=name
  GF_AUTH_GENERIC_OAUTH_USE_PKCE=true
```

#### Pocket ID

Refer to [this page](https://pocket-id.org/docs/client-examples/grafana) on Pocket ID's documentation for the instruction.

### Extending the configuration

There are some additional things you may wish to configure about the service.

Take a look at:

- [`defaults/main.yml`](../defaults/main.yml) for some variables that you can customize via your `vars.yml` file. You can override settings (even those that don't have dedicated playbook variables) using the `grafana_environment_variables_additional_variables` variable

## Installing

After configuring the playbook, run the installation command of your playbook as below:

```sh
ansible-playbook -i inventory/hosts setup.yml --tags=setup-all,start
```

If you use the MASH playbook, the shortcut commands with the [`just` program](https://github.com/mother-of-all-self-hosting/mash-playbook/blob/main/docs/just.md) are also available: `just install-all` or `just setup-all`

## Usage

After running the command for installation, Grafana becomes available at the specified hostname like `https://example.com`.

To get started, open the URL with a web browser, and follow the set up wizard.

## Troubleshooting

### Check the service's logs

You can find the logs in [systemd-journald](https://www.freedesktop.org/software/systemd/man/systemd-journald.service.html) by logging in to the server with SSH and running `journalctl -fu grafana` (or how you/your playbook named the service, e.g. `mash-grafana`).
