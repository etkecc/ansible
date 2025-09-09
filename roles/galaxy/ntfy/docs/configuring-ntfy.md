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

This is an [Ansible](https://www.ansible.com/) role which installs a [ntfy](https://ntfy.sh/) (pronounced "notify") push notification server to run as a [Docker](https://www.docker.com/) container wrapped in a systemd service.

ntfy lets you send push notifications to your phone or desktop via scripts from any computer, using simple HTTP PUT or POST requests. It enables you to send/receive notifications, without relying on servers owned and controlled by third parties.

See the project's [documentation](https://docs.ntfy.sh/) to learn what ntfy does and why it might be useful to you.

**Note**: you need to install [the ntfy Android/iOS app](https://docs.ntfy.sh/subscribe/phone/) on your device in order to receive push notifications from the ntfy server. Notifications can also be sent/received on the ntfy's web app. Refer [this section](#usage) for details about how to use the apps.

## Implementation

### UnifiedPush support

⚠️ [UnifiedPush does not work on iOS.](https://unifiedpush.org/users/faq/#will-unifiedpush-ever-work-on-ios)

ntfy implements [UnifiedPush](https://unifiedpush.org), the standard which makes it possible to send and receive push notifications without using Google's Firebase Cloud Messaging (FCM) service.

Working as a **Push Server**, a ntfy server can forward messages to a **Distributor** running on Android and other devices (see [definitions on the official documentation of UnifiedPush](https://unifiedpush.org/users/distributors/#definitions) for the definition of the Push Server and the Distributor).

This role installs and manages a self-hosted ntfy server as the Push Server, which the Distributor (such as the ntfy Android app) on your device listens to.

Your UnifiedPush-compatible applications (such as [Tusky](https://tusky.app/) and [DAVx⁵](https://www.davx5.com/)) listen to the Distributor, and push notifications are "distributed" from it. This means that the UnifiedPush-compatible applications cannot receive push notifications from the Push Server without the Distributor.

As the ntfy Android app functions as the Distributor too, you do not have to install something else on your device.

💡 **Notes**:

- Refer [this official documentation of UnifiedPush](https://unifiedpush.org/users/troubleshooting/#understand-unifiedpush) for a simple explanation about relationship among UnifiedPush-compatible application, Distributor, Push Server, and the application's server.
- See [this page](https://unifiedpush.org/users/apps/) for a non-exhaustive list of the end-user applications that use UnifiedPush.
- Unlike push notifications using Google's FCM or Apple's APNs, each end-user can choose the Push Server which one prefer. This means that deploying a ntfy server cannot enforce a UnifiedPush-compatible application (and its users) to use the exact server.

### iOS instant notification

Because iOS heavily restricts background processing, it is impossible to implement instant push notifications without a central server.

To implement instant notification through the self-hosted ntfy server, see [this official documentation](https://docs.ntfy.sh/config/#ios-instant-notifications) for instructions.

## Adjusting the playbook configuration

To enable a ntfy server with this role, add the following configuration to your `vars.yml` file.

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

**By default, the ntfy server is open for everyone, meaning anyone can read and write to any topic.** To restrict access to it, you can optionally configure authentication with [access control](https://docs.ntfy.sh/config/#access-control).

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

See [this section](https://docs.ntfy.sh/config/#access-control) on the official documentation about authentication.

UnifiedPush requires application servers to be provided anonymous write access to the topic which will be used for pushing messages, according to [this ntfy's documentation](https://docs.ntfy.sh/config/#example-unifiedpush). As this role takes care of the configuration when creating users (see: [tasks/setup_users.yml](../tasks/setup_users.yml)), you do not need to allow it manually by running `ntfy access` command as described on the documentation.

### Enable web app (optional)

The ntfy server can be accessed via its web app where you can subscribe to and push to topics from the browser. Note that since the web app only runs in the browser locally after downloading assets for it, there is not additional security risk of running it (refer [this FAQ entry](https://docs.ntfy.sh/faq/#can-i-disable-the-web-app-can-i-protect-it-with-a-login-screen)).

💡 If you are concerned for abuse of your ntfy server, it is recommended to enable access control with authentication.

The web app is not enabled on this role by default, because it doesn't work when `ntfy_path_prefix` is not `/` (see: <https://github.com/binwiederhier/ntfy/issues/256>).

To enable it, add the following configuration to your `vars.yml` file:

```yaml
ntfy_web_root: "app"
```

### Message cache

By default the ntfy instance is configured to keep notifications in an on-disk cache, so that notifications can be retaied across restarts. The cache file is stored in the directory specified with `ntfy_data_path`.

To use an in-memory cache instead, add the following configuration to your `vars.yml` file:

```yaml
ntfy_cache_file_enabled: false
```

### Allow attachments (optional)

The ntfy server can be configured to allow users to [attach files](https://docs.ntfy.sh/publish/#attachments) to notifications (default: max. 15M per file, 5G in total).

To allow attachments, add the following configuration to your `vars.yml` file:

```yaml
ntfy_attachment_enabled: true
```

Note that attachments are stored as disk cache for **three hours** by default. To change the period, add the following configuration to your `vars.yml` file and adjust the value as below (adapt to your needs):

```yaml
ntfy_attachment_expiry_duration: "10h"
```

### Enable E-mail notification (optional)

The ntfy server can forward [notification messages as email](https://docs.ntfy.sh/publish/#e-mail-notifications) via a SMTP server for outgoing messages. If configured, you can set the `X-Email` header to send messages as email (e.g. `curl -d "This is a test notification to my email address" -H "X-Email: alice@example.com" example.com/example_topic`).

If the web app is enabled, you can forward messages to a specified email address from there as well, creating a notification at the same time.

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

By default, the ntfy server runs without authentication, so it is important to protect the server from abuse or overload. There are various rate limits enabled with the setting file. Under normal usage, ntfy should not encounter those limits at all.

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
ntfy_visitor_email_limit_burst: 16

# The rate at which the bucket is refilled (one email per x).
ntfy_visitor_email_limit_replenish: "1h"
```

#### Exempt specific hosts from rate limiting

It is possible to exempt certain hosts from rate limiting. Exempted hosts can be defined as hostnames, IP addresses or network ranges.

You can define them by adding the following configuration to your `vars.yml` file:

```yaml
ntfy_visitor_request_limit_exempt_hosts_hostnames_custom: []
```

For example, when using the ntfy server for your [Matrix](https://matrix.org) server to send push notifications on UnifiedPush, it is convenient to exempt its hostname from request rate limiting.

To do so, add the following configuration to your `vars.yml` file (adapt to your needs):

```yaml
ntfy_visitor_request_limit_exempt_hosts_hostnames_custom: |
  {{
    ["matrix.example.com"]
  }}
```

**Note**: if you install and manage the ntfy server with the MDAD Ansible playbook, this configuration is not necessary as the hostname of the Matrix server is exempted from rate limiting by default with its [`group_vars/matrix_servers`](https://github.com/spantaleev/matrix-docker-ansible-deploy/blob/master/group_vars/matrix_servers) file.

### Expose an endpoint for Prometheus (optional)

You can configure the ntfy server so that it can expose a `/metrics` endpoint for Prometheus.

To expose the endpoint with the default port, add the following configuration to your `vars.yml` file:

```yaml
ntfy_metrics_default_enabled: true
```

Alternatively, you can expose the endpoint via a specified IP address and/or port by adding the following configuration to your `vars.yml` file (adapt to your needs). `ntfy_metrics_listen_http_host` can be omitted.

```yaml
ntfy_metrics_listen_http_host: 0.0.0.0
ntfy_metrics_listen_http_port: 9090
```

See [this section](https://docs.ntfy.sh/config/#monitoring) on the official documentation for details.

### Extending the configuration

There are some additional things you may wish to configure about the component.

Take a look at:

- [`defaults/main.yml`](../defaults/main.yml) for some variables that you can customize via your `vars.yml` file. You can override settings (even those that don't have dedicated playbook variables) using the `ntfy_configuration_extension_yaml` variable

See [this section on the official documentation](https://docs.ntfy.sh/config/#config-options) for a complete list of ntfy config options that you could put in `ntfy_configuration_extension_yaml`.

## Installing

After configuring the playbook, run the installation command of your playbook as below:

```sh
ansible-playbook -i inventory/hosts setup.yml --tags=setup-all,start
```

If you use the MDAD / MASH playbook, the shortcut commands with the [`just` program](https://github.com/spantaleev/matrix-docker-ansible-deploy/blob/master/docs/just.md) are also available: `just install-all` or `just setup-all`

## Usage

To receive push notifications from the ntfy server, you need to **install [the ntfy Android/iOS app](https://docs.ntfy.sh/subscribe/phone/)** and then **subscribe to a topic** where messages will be published. You can also send/receive notifications on the ntfy's web app at `example.com`.

### Install the ntfy Android/iOS app

To set up the Android app, you can follow the steps below:

1. Install the [ntfy Android app](https://docs.ntfy.sh/subscribe/phone/) from F-droid or Google Play.
2. In its Settings -> `General: Default server`, enter the ntfy server URL, such as `https://ntfy.example.com`.
3. In its Settings -> `Advanced: Connection protocol`, choose `WebSockets`.

If you are setting up the iOS app, download the app [from this page](https://apps.apple.com/us/app/ntfy/id1625396347) and follow the same steps.

### Log in to your account (optional)

If you have enabled [the access control](#enable-access-control-with-authentication-optional), **you need to log in to the account on the ntfy app**. Otherwise, it will not be able to receive notifications for either itself or UnifiedPush-compatible applications on the device.

To log in to the account on the Android/iOS app, go to the `Settings` on its UI, `General` → `Manage users` → `Add new user`, then input the service URL, the username and password. To the service URL, specify `https://example.com` (the same value as `ntfy_hostname`).

If you use the web app, go to the Settings from its main UI, and click the "Add user" anchor link on the "Manage users" section to log in.

### Subscribe to a topic

*This step can be skipped if you use the app solely as a Distributor for UnifiedPush-compatible applications.*

After installing the app, you can create or subscribe to a topic where messages will be published. **Because anyone can subscribe a topic (unless authentication is enabled), choose ones which cannot be guessed easily.**

After subscribing to a topic (e.g. `SR34vLnN`), you can make sure that your installation is properly configured by sending a test message to it with a POST request as below:

```sh
curl -d "Test notification 🔔" https://example.com/SR34vLnN
```

If everything works as expected, it will create a notification on your device.

### Web App

The web app lets you subscribe and publish messages to ntfy topics. To use it, you can do so by going to the hostname specified above (`example.com`) on the browser.

See [this page](https://docs.ntfy.sh/subscribe/web/) of the official documentation for details about how to use the web app.

#### Progressive Web App (PWA)

ntfy is built as [progressive web app (PWA)](https://docs.ntfy.sh/subscribe/pwa/), which can be installed **both on desktop and mobile devices**. See [this section](https://docs.ntfy.sh/subscribe/web/#background-notifications) for more information.

### UnifiedPush-compatible application

To receive push notifications on a UnifiedPush-compatible application, it must be able to communicate with the ntfy Android app which works as the Distributor on the same device.

Consult to documentation of applications for instruction about how to enable UnifiedPush support. Note that some applications quietly detect and use the Distributor, so you do not always have to configure the applications.

If you are configuring UnifiedPush on a [Matrix](https://matrix.org) client, you can refer [this section](https://github.com/spantaleev/matrix-docker-ansible-deploy/blob/master/docs/configuring-playbook-ntfy.md#setting-up-a-unifiedpush-compatible-matrix-client) on MDAD playbook's documentation.

## Troubleshooting

The simple [UnifiedPush troubleshooting](https://unifiedpush.org/users/troubleshooting/) app [UP-Example](https://f-droid.org/en/packages/org.unifiedpush.example/) can be used to manually test UnifiedPush registration and operation on an Android device.

### Check the service's logs

You can find the logs in [systemd-journald](https://www.freedesktop.org/software/systemd/man/systemd-journald.service.html) by logging in to the server with SSH and running `journalctl -fu ntfy` (or how you/your playbook named the service, e.g. `mash-ntfy`, `matrix-ntfy`).

#### Increase logging verbosity

If you want to increase the verbosity, add the following configuration to your `vars.yml` file and re-run the playbook:

```yaml
ntfy_configuration_extension_yaml: |
  log_level: DEBUG
```
