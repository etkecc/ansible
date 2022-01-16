[![Matrix](https://img.shields.io/matrix/news:etke.cc?logo=matrix&server_fqdn=matrix.org&style=for-the-badge)](https://matrix.to/#/#discussion:etke.cc)[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/etkecc)

It's a wrapper around awesome [spantaleev/matrix-docker-ansible-deploy](https://github.com/spantaleev/matrix-docker-ansible-deploy) playbook
with additional roles and playbooks, like system maintenance (check the list below).

**NOTE**: we have [paid service - etke.cc](https://etke.cc/#contact) - that will do all setup, configuration, and maintenance for you.
That service is pretty cheap and has 2 purposes - invite new people to matrix and support the project.

# Fork differences

## Automatic versions

Used components' version automatically added to the [VERSIONS.md](./VERSIONS.md) file on each commit.

<details>
<summary>How?</summary>

```bash
#!/bin/sh
grep -rhE "^matrix_.*_version: |^custom_.*_version: " ./upstream/roles/*/defaults/main.yml ./roles/*/*/defaults/main.yml | sed -e "s/matrix_//;s/custom_//;s/_version//;/^synapse_default/d;/^synapse_ext/d;/^mailer_container/d" | sort | yq eval -M -P | sed "s/^/\*\ /" > $PWD/VERSIONS.md
git add $PWD/VERSIONS.md
```

> **NOTE**: requires [yq](https://github.com/mikefarah/yq)

</details>

## New roles

### System

> all system roles available in [roles/system](./roles/system).
> Each role has a README.md file with a description and basic how-to.

* **swap** - automatically create and mount swap partition, based on host RAM
* **security** - sshd hardening, fail2ban and ufw installation, automatic integration with other services/roles.
* **maintenance** - system package updates, cleanup, etc. The same for matrix components

### Matrix

> all matrix roles available in [roles/matrix](./roles/matrix).
> Each role has a README.md file with description and basic how-to.

* <s>**cinny** - [cinny.in](https://cinny.in) matrix web client installation</s> uploaded to upstream
* <s>nginx-proxy-health</s> - simple healthcheck, based on systemd units. Works pretty bad, don't use it.
* **nginx-proxy-website** - host a static website on your base domain. Pull it from a git repo, run an arbitrary command (like `hugo`) and upload the results to your server
* **restart** - one-by-one restarts (opposed to the `--tags start` that will stop all the services and start them after that)

### Non-Matrix components

* **dnsmasq** - recursive resolver with adblocker, like pi-hole, but even better! Automatic integration with wireguard
* <s>**honoroit** - [a helpdesk bot](https://gitlab.com/etke.cc/honoroit) to proxy user messages in 1:1 rooms into one big room with threads (check the link, it has pretty cool screenshots).</s> uploaded to upstream
* **kuma** - uptime-kuma monitoring servers. Pretty simple, yet powerful.
* **languagetool** - "open-source grammarly" server
* **miniflux** - an opinionated RSS reader
* **miounne** - [an etke.cc back office](https://gitlab.com/etke.cc/miounne)
* **radicale** - a CalDav/CardDav server, very small and straightforward. It must be in the suckless.org lists!
* **wireguard** - simple and fast VPN, has automatic integration with dnsmasq

### Integration to 3rdParty services

* **git2bunny** - like the `matrix/nginx-proxy-website`, but the target is your BunnyCDN storage
* <s>uptimerobot</s> - automatically create monitors in UptimeRobot. Works pretty bad, don't use it.

# Usage

<details>
<summary>Quick Start</summary>

1. Decide what the domain name will be used for your matrix server ("pretty" domain, like "gitlab.com" or "issuperstar.com" so your mxid will be like "@john:issuperstar.com"), replace `DOMAIN` below with that domain name
2. Run the following commands and read instructions

```bash
# clone that repo
git clone https://gitlab.com/etke.cc/ansible.git
cd ansible

# pull the spantaleev/matrix-docker-ansible-deploy repo
git submodule update --init --recursive

# create directory for your server config
mkdir inventory/host_vars/DOMAIN

# copy the example configs
cp upstream/examples/hosts inventory/hosts
cp upstream/examples/vars.yml inventory/host_vars/DOMAIN/

# edit inventory file and put your server connection details (vim is optional, aye).
# note: replace matrix.<your-domain> with your DOMAIN (tbh, you dont need matrix. prefix here, so you may remove it, too)
vim inventory/hosts

# edit your server configuration file (vim is optional here)
vim inventory/host_vars/DOMAIN/vars.yml
```

and now, follow the [spantaleev/matrix-docker-ansible-deploy documentation](https://github.com/spantaleev/matrix-docker-ansible-deploy/blob/master/docs/README.md)

**NOTE**: For initial server setup use playbook `play/all.yml` (yep, with tags as described in parent project's documentation),
after that you can use playbook `play/matrix.yml`, here is the list of commands to finish initial setup

```bash
# Moving to the grand finale

# Run server setup
ansible-playbook play/all.yml -t setup-all

# create users, configure dimension, etc. - do all the stuff

# Start the server
ansible-playbook play/matrix.yml -t start

# Check if it works
ansible-playbook play/matrix.yml -t self-check
```

</details>

<details>
<summary>Upgrades & maintenance</summary>

New versions of matrix-related software are releaseed very often, so to stay up to date, follow these steps:

* Check parent project's [CHANGELOG](https://github.com/spantaleev/matrix-docker-ansible-deploy/blob/master/CHANGELOG.md) for news
* Upgrade playbooks and roles with `git pull`
* **Don't forget to carefully read the changelog**, because it may contain breaking changes!
* Run the upgrade: `ansible-playbook play/all.yml -t setup-all,start`
* Check if it works as expected: `ansible-playbook play/matrix.yml -t self-check`

### Full maintenance cycle:

1. Run all playbooks (including cleanup tasks)
2. Run rust-synapse-compress-state
3. Run postgres full vacuum.

```bash
ansible-playbook play/all.yml -t setup-all
ansible-playbook play/all.yml -t rust-synapse-compress-state
ansible-playbook play/all.yml -t run-postgres-vacuum
```
</details>

## Supported distros

[Parent project prerequisites](https://github.com/spantaleev/matrix-docker-ansible-deploy/blob/master/docs/prerequisites.md#prerequisites) have a list of supported distributives and versions.
