<!--
SPDX-FileCopyrightText: 2018 - 2024 Slavi Pantaleev
SPDX-FileCopyrightText: 2019 Eduardo Beltrame
SPDX-FileCopyrightText: 2020 - 2025 MDAD project contributors
SPDX-FileCopyrightText: 2024 - 2025 Suguru Hirahara

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# Setting up exim-relay

This is an [Ansible](https://www.ansible.com/) role which installs the [Exim](https://www.exim.org/) mailer via [exim-relay](https://github.com/devture/exim-relay) to run as a [Docker](https://www.docker.com/) container wrapped in a systemd service.

## Prerequisites

To use exim-relay, make sure you have configured the firewall properly. You'll probably need to allow outgoing traffic for TCP ports 25/587 (depending on configuration) on your server if you have not.

## Adjusting the playbook configuration

To enable exim-relay with this role, add the following configuration to your `vars.yml` file.

**Notes**:
- The path should be something like `inventory/host_vars/mash.example.com/vars.yml` if you use the [MASH (Mother-of-All-Self-Hosting)](https://github.com/mother-of-all-self-hosting/mash-playbook) Ansible playbook.
- If you use the MDAD (matrix-docker-ansible-deploy) playbook, these settings are not needed as they are specified by default. See its [`matrix_servers`](https://github.com/spantaleev/matrix-docker-ansible-deploy/blob/master/group_vars/matrix_servers) for details.

```yaml
########################################################################
#                                                                      #
# exim_relay                                                           #
#                                                                      #
########################################################################

exim_relay_enabled: true
exim_relay_hostname: example.com
exim_relay_sender_address: "example@{{ exim_relay_hostname }}"

########################################################################
#                                                                      #
# /exim_relay                                                          #
#                                                                      #
########################################################################
```

### Relaying email through another SMTP server

By default, exim-relay attempts to deliver emails directly. This may or may not work, depending on your domain configuration (SPF settings, etc.)

**On some cloud providers such as Google Cloud, [port 25 is always blocked](https://cloud.google.com/compute/docs/tutorials/sending-mail/), so sending email directly from your server is not possible.** In this case, you will need to relay email through another SMTP server by adding the following configuration to your `vars.yml` file (adapt to your needs):

```yaml
exim_relay_sender_address: "another.sender@example.com"
exim_relay_relay_use: true
exim_relay_relay_host_name: "mail.example.com"
exim_relay_relay_host_port: 587
exim_relay_relay_auth: true
exim_relay_relay_auth_username: "another.sender@example.com"
exim_relay_relay_auth_password: "PASSWORD_FOR_THE_RELAY_HERE"
```

**Note**: only the secure submission protocol (using `STARTTLS`, usually on port `587`) is supported. **SMTPS** (encrypted SMTP, usually on port `465`) **is not supported**.

#### Sending emails using Sendgrid

An easy and free SMTP service to set up is [Sendgrid](https://sendgrid.com/). Its free tier allows for up to 100 emails per day to be sent.

To set it up, add the following configuration to your `vars.yml` file (adapt to your needs):

```yaml
exim_relay_sender_address: "example@example.org"
exim_relay_relay_use: true
exim_relay_relay_host_name: "smtp.sendgrid.net"
exim_relay_relay_host_port: 587
exim_relay_relay_auth: true

# This needs to be literally the string "apikey". It is always the same for Sendgrid.
exim_relay_relay_auth_username: "apikey"

# You can generate the API key password at this URL: https://app.sendgrid.com/settings/api_keys
# The password looks something like `SG.955oW1mLSfwds7i9Yd6IA5Q.q8GTaB8q9kGDzasegdG6u95fQ-6zkdwrPP8bOeuI`.
exim_relay_relay_auth_password: "YOUR_API_KEY_PASSWORD_HERE"
```

### Enable DKIM support (optional)

Exim-relay supports DomainKeys Identified Mail (DKIM) as email authentication method.

To enable it, at first you need to create a DKIM key pair, then add its **public key** to your domain's DNS record. Look on the internet for a guide about how to do so.

After that, add the following configuration to your `vars.yml` file. Make sure to replace `DKIM_PRIVATE_KEY_HERE` with your DKIM's **private key**.

```yaml
exim_relay_dkim_privkey_contents: "DKIM_PRIVATE_KEY_HERE"
```

> [!WARNING]
> DKIM support cannot be activated when it is enabled to [relay email through another SMTP server](#relaying-email-through-another-smtp-server).

## Installing

After configuring the playbook, run the installation command of your playbook as below:

```sh
ansible-playbook -i inventory/hosts setup.yml --tags=setup-all,start
```

If you use the MASH or MDAD Ansible playbook, the shortcut commands with the [`just` program](https://github.com/spantaleev/matrix-docker-ansible-deploy/blob/master/docs/just.md) are also available: `just install-all` or `just setup-all`

## Troubleshooting

If you're having trouble with email not being delivered, it may be useful to inspect the mailer logs.

To do so, log in to the server with SSH and run `journalctl -fu exim-relay` (or how you/your playbook named the service, e.g. `matrix-exim-relay`).
