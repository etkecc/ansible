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

* git branch: `main`
* docker tag: `latest`

"Stable" branch, deployed and tested at least on 1 homeserver.

## Automatic versions

Used components' version automatically added to the [VERSIONS.md](./VERSIONS.md) file on each commit.

How? [bin/versions.py](./bin/versions.py)

## Different focus

The original playbook's focus is on matrix components only, while we at [etke.cc](https://etke.cc) focusing on wider list of goals:

* system security
* maintenance of the operating system
* diversity of the components, including both [matrix](https://github.com/spantaleev/matrix-docker-ansible-deploy) and [non-matrix](https://github.com/mother-of-all-self-hosting/mash-playbook) components

</details>

# Prerequisites

* [git](https://git-scm.com/) - it's a git repo, you know
* [agru](https://github.com/etkecc/agru) - to update roles
* [just](https://just.systems/man/en/) - to automate routine
* [docker](https://www.docker.com/) - to build containers
* [skopeo](https://github.com/containers/skopeo) - to sync containers
* [python](https://www.python.org/) - to run the playbook, build opml, etc.
* [ansible](https://www.ansible.com/) - to run the playbook

# Usage

<details>
<summary>Quick Start</summary>

1. Decide what the domain name will be used for your matrix server ("pretty" domain, like "gitlab.com" or "issuperstar.com" so your mxid will be like "@john:issuperstar.com"), replace `DOMAIN` below with that domain name
2. Run the following commands and read instructions

```bash
# clone that repo
git clone https://github.com/etkecc/ansible.git
cd ansible

# create directory for your server config
mkdir inventory/host_vars/DOMAIN

# copy the example configs
cp .config/examples/hosts inventory/hosts
cp .config/examples/vars.yml inventory/host_vars/DOMAIN/

# edit inventory file and put your server connection details (vim is optional, aye).
# note: replace DOMAIN with your actual base/apex domain name
vim inventory/hosts

# edit your server configuration file
vim inventory/host_vars/DOMAIN/vars.yml
```

and now, follow the [spantaleev/matrix-docker-ansible-deploy documentation](https://github.com/spantaleev/matrix-docker-ansible-deploy/blob/master/docs/README.md)

**NOTE**: For initial server setup use playbook `play/all.yml` (yep, with tags as described in parent project's documentation),
after that you can use playbook `play/matrix.yml`, here is the list of commands to finish initial setup

```bash
# Moving to the grand finale

# Run server setup
just setup-all
```

</details>

## Supported distros

[Parent project prerequisites](https://github.com/spantaleev/matrix-docker-ansible-deploy/blob/master/docs/prerequisites.md#prerequisites) have a list of supported distributives and versions.
