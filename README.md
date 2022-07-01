[![Matrix](https://img.shields.io/matrix/news:etke.cc?logo=matrix&server_fqdn=matrix.org&style=for-the-badge)](https://matrix.to/#/#discussion:etke.cc)[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/etkecc)

It's a wrapper around awesome [spantaleev/matrix-docker-ansible-deploy](https://github.com/spantaleev/matrix-docker-ansible-deploy) playbook
with additional roles and playbooks, like system maintenance (check the list below).

**NOTE**: we have [paid service - etke.cc](https://etke.cc/) - that will do all setup, configuration, and maintenance for you.
That service is pretty cheap and has 2 purposes - invite new people to matrix and support the project.

# Fork differences

## Stability

This repository contains different stability branches (git branches and docker tags)

### fresh

* git branch: `fresh`
* docker tag: `fresh`

Testing branch, with latest updates from the upstream and unstable changes, including new roles

### master

* git branch: `master`
* docker tag: `latest`

"Stable" branch, deployed and tested at least on 1 homeserver.

## Automatic versions

Used components' version automatically added to the [VERSIONS.md](./VERSIONS.md) file on each commit.

How? [commit-msg.sh](./commit-msg.sh)

> **NOTE**: requires [yq](https://github.com/mikefarah/yq)

</details>

## New roles

### System

* **[init](https://gitlab.com/etke.cc/roles/init)** - run arbitrary commands before the play starts
* **swap** - automatically create and mount swap partition, based on host RAM
* **security** - sshd hardening, fail2ban and ufw installation, automatic integration with other services/roles.
* **maintenance** - system package updates, cleanup, etc. The same for matrix components

### Matrix

> all matrix roles available in [roles/matrix](./roles/matrix).
> Each role has a README.md file with description and basic how-to.

* **nginx-proxy-website** - host a static website on your base domain. Pull it from a git repo, run an arbitrary command (like `hugo`) and upload the results to your server
* **restart** - one-by-one restarts (opposed to the `--tags start` that will stop all the services and start them after that)
* **room-purger** - purge matrix rooms through synapse admin api
* **miounne** - deprecated [an old etke.cc back office](https://gitlab.com/etke.cc/miounne)
* <s>**cinny** - [cinny.in](https://cinny.in) matrix web client installation</s> uploaded to upstream
* <s>**honoroit** - [a helpdesk bot](https://gitlab.com/etke.cc/honoroit) to proxy user messages in 1:1 rooms into one big room with threads (check the link, it has pretty cool screenshots).</s> uploaded to upstream
* <s>**buscarron** - [a new etke.cc back office](https://gitlab.com/etke.cc/buscarron)</s> uploaded to upstream
* <s>nginx-proxy-health</s> - deprecated simple healthcheck, based on systemd units. Works pretty bad, don't use it.

### Non-Matrix components

* **dnsmasq** - recursive resolver with adblocker, like pi-hole, but even better! Automatic integration with wireguard
* **kuma** - uptime-kuma monitoring servers. Pretty simple, yet powerful.
* **languagetool** - "open-source grammarly" server
* **miniflux** - an opinionated RSS reader
* **radicale** - a CalDav/CardDav server, very small and straightforward. It must be in the suckless.org lists!
* **soft-serve** - a tasty, self-hostable Git server for the command line
* **wireguard** - simple and fast VPN, has automatic integration with dnsmasq
* **prometheus-blackbox-exporter** - blackbox exporter
* <s>**backup-borg** - automatic borg backups of the matrix server</s> uploaded to upstream

### Integration to 3rdParty services

* **[git2bunny](https://gitlab.com/etke.cc/roles/git2bunny)** - like the `matrix/nginx-proxy-website`, but the target is your BunnyCDN storage

# Usage

<details>
<summary>Quick Start</summary>

1. Decide what the domain name will be used for your matrix server ("pretty" domain, like "gitlab.com" or "issuperstar.com" so your mxid will be like "@john:issuperstar.com"), replace `DOMAIN` below with that domain name
2. Run the following commands and read instructions

```bash
# clone that repo
git clone https://gitlab.com/etke.cc/ansible.git
cd ansible

# pull the spantaleev/matrix-docker-ansible-deploy repo and other dependency roles
make dependencies

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
ansible-playbook play/all.yml -l DOMAIN -t setup-all
ansible-playbook play/all.yml -l DOMAIN -t rust-synapse-compress-state -e matrix_synapse_rust_synapse_compress_state_find_rooms_command_wait_time=86400 -e matrix_synapse_rust_synapse_compress_state_compress_room_time=86400 -e matrix_synapse_rust_synapse_compress_state_psql_import_time=86400
ansible-playbook play/all.yml -l DOMAIN -t run-postgres-vacuum
ansible-playbook play/all.yml -l DOMAIN -t restart-all
```
</details>

## Supported distros

[Parent project prerequisites](https://github.com/spantaleev/matrix-docker-ansible-deploy/blob/master/docs/prerequisites.md#prerequisites) have a list of supported distributives and versions.
