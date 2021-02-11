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

# Install

```bash
git clone https://gitlab.com/rakshazi/matrix-ansible.git
cd matrix-ansible
git submodule update --init --recursive
```
