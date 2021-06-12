[![Matrix](https://img.shields.io/matrix/announcements:etke.cc?logo=matrix&server_fqdn=matrix.org&style=for-the-badge)](https://matrix.to/#/#discuss:etke.cc) [![Buy me a Coffee](https://shields.io/badge/donate-buy%20me%20a%20coffee-green?logo=buy-me-a-coffee&style=for-the-badge)](https://buymeacoffee.com/etkecc)

It's a wrapper around awesome [spantaleev/matrix-docker-ansible-deploy](https://github.com/spantaleev/matrix-docker-ansible-deploy) playbook
with additional roles and playbooks, like system maintenance (check the list below).

**NOTE**: we have [paid service - etke.cc](https://etke.cc/#contact) - that will do all setup, configuration and maintenance for you.
That service pretty cheap and has 2 purposes - invite new people to matrix and support project.

# Included features & perks

## versions

List of used sofrware versions available here: [VERSIONS.md](./VERSIONS.md)

that list generated with pre-commit hook:

```bash
#!/bin/sh
grep -rhE "^matrix_.*_version: |^custom_.*_version: " ./upstream/roles/*/defaults/main.yml ./roles/*/*/defaults/main.yml | sed -e "s/matrix_//;s/custom_//;s/_version//;/^synapse_default/d;/^synapse_ext/d;/^mailer_container/d" | sort | yq -y | sed "s/^/\*\ /" > $PWD/VERSIONS.md
git add $PWD/VERSIONS.md
```

## playbooks

That repo provides following playbooks:

* `play/maintenance.yml` - add swap, update system packages, clean up space
* `play/security.yml` - install and configure fail2ban, ufw and sshd to avoid breaches
* `play/matrix.yml` - symlink to `setup.yml` of [spantaleev/matrix-docker-ansible-deploy](https://github.com/spantaleev/matrix-docker-ansible-deploy)
* `play/website.yml` - deploy your static website to base domain, [website deploy documentation](./roles/matrix/nginx-proxy-website/README.md), [health report documentation](./roles/matrix/nginx-proxy-health/README.md)
* `play/integration.yml` - UptimeRobot integration
* `play/all.yml` - run all the stuff above, usefull when configuring new server

## roles

* `roles/system/maintenance` - used by `play/maintenance.yml`, [documentation](./roles/system/maintenance/README.md)
* `roles/system/security` - used by `play/security.yml`
* `roles/system/swap` - used by `play/maintenance.yml`, [documentation](./roles/system/swap/README.md)
* `roles/matrix/nginx-proxy-health` - used by `play/website.yml`, [documentation](./roles/matrix/nginx-proxy-health/README.md)
* `roles/matrix/nginx-proxy-website` - used by `play/website.yml`, [documentation](./roles/matrix/nginx-proxy-website/README.md)
* `roles/matrix/restart` - used by `play/matrix.yml`
* `roles/custom/wireguard` - used by `play/matrix.yml`, [documentation](./roles/custom/wireguard/README.md)
* `roles/custom/miniflux` - used by `play/matrix.yml`, [documentation](./roles/custom/miniflux/README.md)
* `roles/custom/languagetool` - used by `play/matrix.yml`, [documentation](./roles/custom/languagetool/README.md)
* `roles/integration/uptimerobot` - used by `play/integration`, [documentation](./roles/integration/uptimerobot/README.md)

# Usage

## Configure new server

1. Decide what the domain name will be used for your matrix server ("pretty" domain, like: "gitlab.com" or "issuperstar.com" so your mxid will be like "@john:issuperstar.com"), replace `DOMAIN` below with that domain name
2. Run the following commands and read instructions

```bash
# clone that repo
git clone https://gitlab.com/rakshazi/matrix-ansible.git
cd matrix-ansible

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

## Upgrades & maintenance

New versions of matrix-related software releases very often, so to stay up to date, follow these steps:

* Check parent project's [CHANGELOG](https://github.com/spantaleev/matrix-docker-ansible-deploy/blob/master/CHANGELOG.md) for news
* Upgrade playbooks and roles with `git pull`
* **Don't forget to carefuly read changelog**, because it may contains breaking changes!
* Run the upgrade: `ansible-playbook play/all.yml -t setup-all,start`
* Check if it works as expected: `ansible-playbook play/matrix.yml -t self-check`

## Supported distributives

[Parent project prerequisites](https://github.com/spantaleev/matrix-docker-ansible-deploy/blob/master/docs/prerequisites.md#prerequisites)
has a list of supported distributives and versions.

**NOTE**: that repository developing and testing on Ubuntu 18.04 LTS _and following cloud providers: AWS, Digital Ocean, Hetzner_.

I'm trying to avoid distro-specific tools and commands (if such tool/command/module used, it will be called only if `ansible_os_family` allows that),
but again - all development and testing performed only on Ubuntu 18.04 LTS and I cannot guarantee that my "wrapper" will work as expected on any other distro or version.
