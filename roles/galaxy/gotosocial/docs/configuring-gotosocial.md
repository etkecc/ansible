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
SPDX-FileCopyrightText: 2023 Julian-Samuel Gebühr
SPDX-FileCopyrightText: 2023 Pierre 'McFly' Marty
SPDX-FileCopyrightText: 2024 - 2025 Suguru Hirahara

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# Setting up GotoSocial

This is an [Ansible](https://www.ansible.com/) role which installs [GotoSocial](https://gotosocial.org/) to run as a [Docker](https://www.docker.com/) container wrapped in a systemd service.

GoToSocial is a self-hosted [ActivityPub](https://activitypub.rocks/) social network server. With GoToSocial, you can keep in touch with your friends, post, read, and share images and articles.

See the project's [documentation](https://docs.gotosocial.org/) to learn what GotoSocial does and why it might be useful to you.

## Prerequisites

To run a GotoSocial instance it is necessary to prepare a [Postgres](https://www.postgresql.org) database server.

If you are looking for an Ansible role for it, you can check out [this role (ansible-role-postgres)](https://github.com/mother-of-all-self-hosting/ansible-role-postgres) maintained by the [Mother-of-All-Self-Hosting (MASH)](https://github.com/mother-of-all-self-hosting) team.

## Adjusting the playbook configuration

To enable GoToSocial with this role, add the following configuration to your `vars.yml` file.

**Note**: the path should be something like `inventory/host_vars/mash.example.com/vars.yml` if you use the [MASH Ansible playbook](https://github.com/mother-of-all-self-hosting/mash-playbook).

```yaml
########################################################################
#                                                                      #
# gotosocial                                                           #
#                                                                      #
########################################################################

gotosocial_enabled: true

########################################################################
#                                                                      #
# /gotosocial                                                          #
#                                                                      #
########################################################################
```

### Set the hostname

To enable the GoToSocial instance you need to set the hostname as well. To do so, add the following configuration to your `vars.yml` file. Make sure to replace `example.com` with your own value.

```yaml
gotosocial_hostname: "social.example.com"
```

> [!WARNING]
> Do not replace the value after the GoToSocial instance has already run once. If changed, it stops working properly.

After adjusting the hostname, make sure to adjust your DNS records to point the domain to your server.

**Note**: hosting GoToSocial under a subpath (by configuring the `gotosocial_path_prefix` variable) does not seem to be possible due to GoToSocial's technical limitations.

#### Set a shorter domain for your handle (optional)

On ActivityPub-powered platforms like GoToSocial, the user handle consists of two parts: username and server. For example, if your handle is `@user@social.example.com`, `user` is the username and `social.example.com` indicates the server.

By default, GoToSocial uses `gotosocial_hostname` that you provide for the server's domain, but you can use a shorter one without the subdomain (`example.com`) by adding the following configuration to your `vars.yml` file:

```yaml
gotosocial_account_domain: "example.com"
```

> [!WARNING]
> Do not replace the value after the GoToSocial instance has already run once. If changed, it stops working properly.

**Note**: if you enable it, please have a look at [this page on the official documentation](https://docs.gotosocial.org/en/latest/advanced/host-account-domain/) as you will have to configure the instance for it.

### Set variables for connecting to a Postgres database server

To use a Postgres server, add the following configuration to your `vars.yml` file.

```yml
gotosocial_database_hostname: YOUR_POSTGRES_SERVER_HOSTNAME_HERE
gotosocial_database_port: 5432
gotosocial_database_name: YOUR_POSTGRES_SERVER_DATABASE_NAME_HERE
gotosocial_database_username: YOUR_POSTGRES_SERVER_USERNAME_HERE
gotosocial_database_password: YOUR_POSTGRES_SERVER_PASSWORD_HERE
```

Make sure to replace values for variables with yours.

### Configure the mailer

You can configure a SMTP mailer for functions such as sending notifications. To set it up, add the following configuration to your `vars.yml` file as below (adapt to your needs):

```yaml
# Set the hostname of the SMTP server
gotosocial_smtp_host: 'smtp.example.com'

# Set the username for the SMTP server
gotosocial_smtp_username: gotosocial@example.com

# Set the password for the SMTP server
gotosocial_smtp_password: yourpassword

# Set the email address that emails will be sent from
gotosocial_smtp_from: gotosocial@example.com
```

⚠️ **Note**: without setting an authentication method such as DKIM, SPF, and DMARC for your hostname, emails are most likely to be quarantined as spam at recipient's mail servers. If you have set up a mail server with the [MASH project's exim-relay Ansible role](https://github.com/mother-of-all-self-hosting/ansible-role-exim-relay), you can enable DKIM signing with it. Refer [its documentation](https://github.com/mother-of-all-self-hosting/ansible-role-exim-relay/blob/main/docs/configuring-exim-relay.md#enable-dkim-support-optional) for details.

### Extending the configuration

There are some additional things you may wish to configure about the component.

Take a look at:

- [`defaults/main.yml`](../defaults/main.yml) for some variables that you can customize via your `vars.yml` file. You can override settings (even those that don't have dedicated playbook variables) using the `gotosocial_environment_variables_additional_variables` variable

See [this page](https://docs.gotosocial.org/en/latest/configuration/#environment-variables) of the official documentation for GoToSocial's config options that you could put in `gotosocial_environment_variables_additional_variables`.

## Installing

After configuring the playbook, run the installation command of your playbook as below:

```sh
ansible-playbook -i inventory/hosts setup.yml --tags=setup-all,start
```

If you use the MASH playbook, the shortcut commands with the [`just` program](https://github.com/mother-of-all-self-hosting/mash-playbook/blob/main/docs/just.md) are also available: `just install-all` or `just setup-all`

## Usage

After running the command for installation, you can create user account(s).

Run this command to create an **administrator** user account:

```sh
ansible-playbook -i inventory/hosts setup.yml --tags=gotosocial-add-admin --extra-vars=username=YOUR_USERNAME_HERE --extra-vars=password=YOUR_PASSWORD_HERE --extra-vars=email=YOUR_EMAIL_ADDRESS_HERE
```

Run this command to create a **regular** (non-administrator) user account:

```sh
ansible-playbook -i inventory/hosts setup.yml --tags=gotosocial-add-user --extra-vars=username=YOUR_USERNAME_HERE --extra-vars=password=YOUR_PASSWORD_HERE --extra-vars=email=YOUR_EMAIL_ADDRESS_HERE
```

Now you should be able to visit the URL at the specified hostname like `https://social.example.com` and check your instance.

To customize your instance, go to the `/admin` page.

### GoToSocial CLI tool

You can use the [GtS CLI tool](https://docs.gotosocial.org/en/latest/admin/cli/) to conduct administration and maintenance tasks.

For example, you can demote a user from an admin user to a normal user by running the command below **on the server**:

```sh
docker exec -it gotosocial /gotosocial/gotosocial admin account demote --username USERNAME_HERE
```

## Migrate an existing instance

If you want to migrate your existing GoToSocial instance to another server, you can follow the procedure described as below.

**Note**: the following assumes you will migrate from **serverA** to **serverB**. Adjust the commands for copying files, if you are migrating on the same server (from an existing GoToSocial instance to the new one to start managing it with a playbook, for example).

### Stop the existing instance

First, stop the existing instance by logging in to **serverA** with SSH and running the command below.

```sh
serverA$ systemctl stop gotosocial
```

### Dump database

Then, dump the database by running the command below. Note that you might have to adjust the command, depending on your existing installation.

```
serverA$ pg_dump gotosocial > latest.sql
```

### Copy files to the new server

After dumping the database, let's copy data to a new server by using a tool such as `rsync`. To do so, log in to **serverA** with SSH, install it if not available, and then run the commands below.

```sh
serverA$ rsync -av -e "ssh" latest.sql root@serverB:/gotosocial/

serverA$ rsync -av -e "ssh" data/* root@serverB:/gotosocial/data/
```

Make sure to change the paths as necessary.

>[!NOTE]
> If you use the MASH Ansible playbook, the paths should be set to `/mash/gotosocial/` instead of `/gotosocial/`.

### Install the service

Next, install the service by running the playbook as below on your local computer:

```sh
yourPC$ ansible-playbook -i inventory/hosts setup.yml --tags=install-all
```

**Do not run `start` tag yet.** Otherwise, the database could not be imported properly.

### Import the database

After installing it, import the database by running the playbook as below:

```sh
yourPC$ ansible-playbook -i inventory/hosts setup.yml --tags=import-postgres --extra-vars=server_path_postgres_dump=/gotosocial/latest.sql --extra-vars=postgres_default_import_database=YOUR_POSTGRES_SERVER_DATABASE_NAME_HERE
```

Make sure to change the path and replace `YOUR_POSTGRES_SERVER_DATABASE_NAME_HERE` with yours (specified with `gotosocial_database_name`).

>[!NOTE]
> If you use the MASH Ansible playbook, run this command to import the database: `ansible-playbook -i inventory/hosts setup.yml --tags=import-postgres --extra-vars=server_path_postgres_dump=/mash/gotosocial/latest.sql --extra-vars=postgres_default_import_database=mash-gotosocial`

### Start the services

After importing the database have completed, start the services by running the playbook:

```sh
yourPC$ ansible-playbook -i inventory/hosts setup.yml --tags=start
```

## Troubleshooting

### Check the service's logs

You can find the logs in [systemd-journald](https://www.freedesktop.org/software/systemd/man/systemd-journald.service.html) by logging in to the server with SSH and running `journalctl -fu gotosocial` (or how you/your playbook named the service, e.g. `mash-gotosocial`).
