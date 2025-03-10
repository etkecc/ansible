<!--
SPDX-FileCopyrightText: 2020 - 2024 MDAD project contributors
SPDX-FileCopyrightText: 2020 - 2024 Slavi Pantaleev
SPDX-FileCopyrightText: 2020 Aaron Raimist
SPDX-FileCopyrightText: 2020 Chris van Dijk
SPDX-FileCopyrightText: 2020 Dominik Zajac
SPDX-FileCopyrightText: 2020 Mickaël Cornière
SPDX-FileCopyrightText: 2022 François Darveau
SPDX-FileCopyrightText: 2022 Julian Foad
SPDX-FileCopyrightText: 2022 Warren Bailey
SPDX-FileCopyrightText: 2023 Antonis Christofides
SPDX-FileCopyrightText: 2023 Felix Stupp
SPDX-FileCopyrightText: 2023 Pierre 'McFly' Marty
SPDX-FileCopyrightText: 2024 - 2025 Suguru Hirahara

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# Setting up ntfy

This is an [Ansible](https://www.ansible.com/) role which installs [ntfy](https://ntfy.sh/) to run as a [Docker](https://www.docker.com/) container wrapped in a systemd service.

Using the [UnifiedPush](https://unifiedpush.org) standard, ntfy enables self-hosted (Google-free) push notifications from servers to UnifiedPush-compatible apps running on Android and other devices.

See the project's [documentation](https://docs.ntfy.sh/) to learn what ntfy does and why it might be useful to you.

**Note**: In contrast to push notifications using Google's FCM or Apple's APNs, the use of UnifiedPush allows each end-user to choose the push notification server that they prefer. As a consequence, deploying this ntfy server does not by itself ensure any particular user or device or client app will use it.

## Adjusting the playbook configuration

To enable ntfy with this role, add the following configuration to your `vars.yml` file.

**Note**: the path should be something like `inventory/host_vars/matrix.example.com/vars.yml` if you use the [matrix-docker-ansible-deploy (MDAD)](https://github.com/spantaleev/matrix-docker-ansible-deploy) or [Mother-of-All-Self-Hosting (MASH)](https://github.com/mother-of-all-self-hosting/mash-playbook) Ansible playbook.


```yaml
########################################################################
#                                                                      #
# ntfy                                                                 #
#                                                                      #
########################################################################

ntfy_enabled: true

########################################################################
#                                                                      #
# /ntfy                                                                #
#                                                                      #
########################################################################
```

### Set the hostname

**Note**: if you use the MDAD Ansible playbook, it installs ntfy on the `ntfy.` subdomain (`ntfy.example.com`) by default, so this setting is optional.

To serve ntfy you need to set the hostname as well. To do so, add the following configuration to your `vars.yml` file. Make sure to replace `example.com` with your own value.

```yaml
ntfy_hostname: "example.com"
```

After adjusting the hostname, make sure to adjust your DNS records to point the ntfy domain to your server.

### Enable access control with authentication (optional)

By default, the ntfy server is open for everyone, meaning anyone can read and write to any topic. To restrict access to your ntfy instance, you can optionally configure authentication.

To enable authentication, add users with a username and password to `ntfy_credentials` on your `vars.yml` file (adapt to your needs):

```yaml
ntfy_credentials:
  - username: user1
    password: password1
    admin: true
  - username: user2
    password: password2
    admin: false
```

If the variable is left empty (`ntfy_credentials: []`), authentication will be disabled, allowing unrestricted access to any topics.

See [here](https://docs.ntfy.sh/config/#access-control) on the official documentation about authentication.

### Enable web app (optional)

ntfy also has a web app where you can subscribe to and push to topics from the browser. The web app only runs in the browser locally (after downloading the JavaScript).

The web app is not enabled on this role by default, because it doesn't work when `ntfy_path_prefix` is not `/` (see: https://github.com/binwiederhier/ntfy/issues/256).

To enable it, add the following configuration to your `vars.yml` file:

```yaml
ntfy_web_root: "app"
```

### Enable E-mail notification (optional)

ntfy can forward notification messages as email via a SMTP server for outgoing messages. If configured, you can set the `X-Email` header to send messages as email (e.g. `curl -d "This is a test notification to my email address" -H "X-Email: alice@example.com" example.com/example_topic`).

If the web app is enabled, you can forward messages to a specified email address, publishing notification at the same time.

To enable it, add the following configuration to your `vars.yml` file (adapt to your needs):

```yaml
ntfy_smtp_sender_enabled: true
ntfy_smtp_sender_addr_host: ''  # Hostname
ntfy_smtp_sender_addr_port: 587
ntfy_smtp_sender_username: ''  # Username of the SMTP user
ntfy_smtp_sender_password: ''  # Password of the SMTP user
ntfy_smtp_sender_from: ''  # Email address of the sender
```

⚠️ **Notes**:
- Your IP address is included in the notification email's body in order to prevent abuse.
- Without setting an authentication method such as DKIM, SPF, and DMARC for your hostname, notification email is most likely to be quarantined as spam at recipient's mail servers. If you have set up a mail server with [our exim-relay Ansible role](https://github.com/mother-of-all-self-hosting/ansible-role-exim-relay), you can enable DKIM signing with it. Refer [its documentation](https://github.com/mother-of-all-self-hosting/ansible-role-exim-relay/blob/main/docs/configuring-exim-relay.md#enable-dkim-support-optional) for details.

### Edit rate limits (optional)

By default, ntfy runs without authentication, so it is important to protect the server from abuse or overload. There are various rate limits enabled with the setting file. Under normal usage, ntfy should not encounter those limits at all.

If necessary, you can configure the limits by adding these variables to your `vars.yml` file and adjusting them:

```yaml
# The total number of topics before the server rejects new topics.
ntfy_global_topic_limit: 15000

# The number of subscriptions (open connections) per visitor.
ntfy_visitor_subscription_limit: 30

# The initial bucket of requests each visitor has.
ntfy_visitor_request_limit_burst: 60

# The rate at which the bucket is refilled (one request per x).
ntfy_visitor_request_limit_replenish: "5s"
```

See [this section](https://docs.ntfy.sh/config/#rate-limiting) on the official documentation for details about them.

#### Edit rate limits for email notification

To prevent abuse, rate limiting for email notification is strict. With the default configuration, 16 messages per visitor (based on IP address) are allowed. After the quota has been exceeded, one message per hour is allowed.

If necessary, you can configure the limits by adding these variables to your `vars.yml` file and adjusting them:

```yaml
# The initial bucket of emails each visitor has.
ntfy_visitor_email_limit_burst: "16"

# The rate at which the bucket is refilled (one email per x).
ntfy_visitor_email_limit_replenish: "1h"
```

#### Exempt specific hosts from rate limiting

It is possible to exempt certain hosts from rate limiting. Exempted hosts can be defined as hostnames, IP addresses or network ranges.

You can define them by adding these variables to your `vars.yml` file (adapt to your needs):

```yaml
ntfy_visitor_request_limit_exempt_hosts_hostnames_custom: []
```

### Extending the configuration

There are some additional things you may wish to configure about the component.

Take a look at:

- [`defaults/main.yml`](../defaults/main.yml) for some variables that you can customize via your `vars.yml` file. You can override settings (even those that don't have dedicated playbook variables) using the `ntfy_configuration_extension_yaml` variable

For a complete list of ntfy config options that you could put in `ntfy_configuration_extension_yaml`, see the [ntfy config documentation](https://docs.ntfy.sh/config/#config-options).

## Installing

After configuring the playbook, run the installation command of your playbook as below:

```sh
ansible-playbook -i inventory/hosts setup.yml --tags=setup-all,start
```

If you use the MDAD / MASH playbook, the shortcut commands with the [`just` program](https://github.com/spantaleev/matrix-docker-ansible-deploy/blob/master/docs/just.md) are also available: `just install-all` or `just setup-all`

## Usage

You can use your self-hosted ntfy server with its application for Android and iOS and/or with its web app (if enabled).

You need to install the `ntfy` app on each device on which you want to receive push notifications through your ntfy server. The `ntfy` app will provide UnifiedPush notifications to any number of UnifiedPush-compatible messaging apps installed on the same device.

### Setting up the `ntfy` Android app

To set up the `ntfy` Android app, you can follow the steps below:

1. Install the [ntfy Android app](https://docs.ntfy.sh/subscribe/phone/) from F-droid or Google Play.
2. In its Settings -> `General: Default server`, enter your ntfy server URL, such as `https://ntfy.example.com`.
3. In its Settings -> `Advanced: Connection protocol`, choose `WebSockets`.

If you are setting up the iOS app, download the app [here](https://apps.apple.com/us/app/ntfy/id1625396347) and follow the same steps.

### Web App

To use the web app, you can do so by going to the hostname specified above (`example.com`) on the browser.

## Troubleshooting

### Check the service's logs

You can find the logs in [systemd-journald](https://www.freedesktop.org/software/systemd/man/systemd-journald.service.html) by logging in to the server with SSH and running `journalctl -fu ntfy` (or how you/your playbook named the service, e.g. `matrix-ntfy`).

#### Increase logging verbosity

If you want to increase the verbosity, add the following configuration to your `vars.yml` file and re-run the playbook:

```yaml
ntfy_configuration_extension_yaml: |
  log_level: DEBUG
```
