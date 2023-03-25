[![Matrix](https://img.shields.io/matrix/news:etke.cc?logo=matrix&server_fqdn=matrix.org&style=for-the-badge)](https://matrix.to/#/#discussion:etke.cc)[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/etkecc)

It's a wrapper around awesome [spantaleev/matrix-docker-ansible-deploy](https://github.com/spantaleev/matrix-docker-ansible-deploy) playbook
with additional roles and playbooks, like system maintenance (check the list below).

This Ansible playbook tries to make self-hosting and maintaining a Matrix server fairly easy. Still, running any service smoothly requires knowledge, time and effort.

If you like the [FOSS](https://en.wikipedia.org/wiki/Free_and_open-source_software) spirit of this Ansible playbook, but prefer to put the responsibility on someone else, you can also [get a managed Matrix server from etke.cc](https://etke.cc/) - a service built on top of this Ansible playbook, which can help you run a Matrix server with ease.

If you like learning and experimentation, but would rather reduce future maintenance effort, you can even go for a hybrid approach - self-hosting manually using this Ansible playbook at first and then transferring server maintenance to etke.cc at a later time.

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

How? [bin/commit-msg.sh](./bin/commit-msg.sh)

> **NOTE**: requires [yq](https://github.com/mikefarah/yq)

## Different focus

The original playbook's focus is on matrix components only, while we at [etke.cc](https://etke.cc) focusing on wider list of goals:

* system security
* maintenance of the operating system
* matrix components (that's the upstream's goal)
* diversity of the components

</details>

# Prerequisites

* [yq](https://github.com/mikefarah/yq) - to generate VERSIONS.md
* [git](https://git-scm.com/) - it's a git repo, you know
* [sed](https://en.wikipedia.org/wiki/Sed) - to generate VERSIONS.md
* [grep](https://en.wikipedia.org/wiki/Grep) - to generate VERSIONS.md
* [agru](https://gitlab.com/etke.cc/int/agru) - to update roles
* [just](https://just.systems/man/en/) - to automate routine
* [docker](https://www.docker.com/) - to build containers
* [skopeo](https://github.com/containers/skopeo) - to sync containers
* [python](https://www.python.org/) - to run the playbook, build opml and hookshot lists
* [ansible](https://www.ansible.com/) - to run the playbook

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
just dependencies

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
