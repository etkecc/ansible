[![Support room on Matrix](https://img.shields.io/matrix/matrix-docker-ansible-deploy:devture.com.svg?label=%23matrix-docker-ansible-deploy%3Adevture.com&logo=matrix&style=for-the-badge&server_fqdn=matrix.devture.com)](https://matrix.to/#/#matrix-docker-ansible-deploy:devture.com)[![donate](https://liberapay.com/assets/widgets/donate.svg)](https://liberapay.com/s.pantaleev/donate)

It's a wrapper around awesome [spantaleev/matrix-docker-ansible-deploy](https://github.com/spantaleev/matrix-docker-ansible-deploy) playbook
with additional tasks, like system Maintenance.

Please, read the [spantaleev/matrix-docker-ansible-deploy](https://github.com/spantaleev/matrix-docker-ansible-deploy) documentation,
because matrix-ansible repo is only a wrapper around it, so 99% of work done in Slavi's repo.

# Included features & perks

## playbooks

That repo provides following playbooks:

* `play/maintenance.yml` - update system packages, clean up space
* `play/security.yml` - install and configure fail2ban, ufw and sshd to avoid breaches
* `play/matrix.yml` - symlink to `setup.yml` of [spantaleev/matrix-docker-ansible-deploy](https://github.com/spantaleev/matrix-docker-ansible-deploy)
* `play/all.yml` - run all the stuff above, usefull when configuring new server

# How to start

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
after that you can use playbook `play/matrix.yml`
