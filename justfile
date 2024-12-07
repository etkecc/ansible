# show help by default
default:
    @just --list --justfile {{ justfile() }}

### Playbook recipes

# Runs the playbook with --tags=install-all,ensure-users-created,start and optional arguments
install-all *extra_args: (run-tags "install-all,ensure-users-created,start" extra_args)

# Runs installation tasks for a single service
install-service service *extra_args:
    just --justfile {{ justfile() }} run \
    --tags=install-{{ service }},start-group \
    --extra-vars=group={{ service }} \
    --extra-vars=devture_systemd_service_manager_service_restart_mode=one-by-one {{ extra_args }}

# Runs the playbook with --tags=setup-all,ensure-users-created,start and optional arguments
setup-all *extra_args: (run-tags "setup-all,ensure-users-created,start" extra_args)

# Rotates SSH keys (uses play/ssh.yml and tags=rotate-ssh-keys)
rotate-ssh-keys +extra_args:
    #!/usr/bin/env sh
    set -eu pipefail
    if [ -x "$(command -v etkepass)" ]; then
        export SSH_ASKPASS=$(which etkepass)
        export SSH_ASKPASS_REQUIRE=force
        export SSH_ASKPASS_DEBUG=1
    fi
    time ansible-playbook play/ssh.yml -t rotate-ssh-keys {{ extra_args }}

# Runs the playbook with the given list of arguments
run +extra_args:
    #!/usr/bin/env sh
    set -eu pipefail
    if [ -x "$(command -v etkepass)" ]; then
        export SSH_ASKPASS=$(which etkepass)
        export SSH_ASKPASS_REQUIRE=force
        export SSH_ASKPASS_DEBUG=1
    fi
    time ansible-playbook play/all.yml {{ extra_args }}

# Runs the playbook with the given list of comma-separated tags and optional arguments
run-tags tags *extra_args:
    just --justfile {{ justfile() }} run --tags={{ tags }} {{ extra_args }}

# Runs the ssh role only with the given list of arguments
run-ssh *extra_args:
    time ansible-playbook play/ssh.yml --tags=install-ssh -e system_security_ssh_enabled=true {{ extra_args }}

### Infrastructure

# run ansible-lint
lint:
    ansible-lint --project-dir . --exclude upstream

# prints roles files for which a GIT feeds couldn't be extracted
nofeeds:
    python bin/feeds.py . check

# pull dependencies
pull-dependencies: pull-submodules pull-roles

# initialize upstream with pinned commit
pull-submodules:
    git submodule update --init --recursive

# pull roles
pull-roles:
    #!/usr/bin/env sh
    set -eu pipefail
    if [ -x "$(command -v agru)" ]; then
        agru ${AGRU_CLEANUP:-}
    else
        ansible-galaxy install -r requirements.yml -p roles/galaxy/ --force
    fi

# pull all updates
update *flags: update-self update-upstream && update-opml update-versions
    @agru {{ flags }}

# dumps an OPML file with extracted git feeds for roles
update-opml:
    @echo "generating opml..."
    @python bin/feeds.py . dump

# pull self
update-self:
    @echo "updating self..."
    @git stash -q
    @git pull -q
    @-git stash pop -q

# merge fresh into main
update-stable:
    @echo "[1/9] force switch to the fresh branch"
    @git checkout fresh

    @echo "[2/9] fetch and apply any missing changes in the local fresh branch"
    @git pull

    @echo "[3/9] switch to the main branch"
    @git checkout main

    @echo "[4/9] fetch and apply any missing changes in the local main branch"
    @git pull

    @echo "[5/9] merge the fresh branch into the main branch"
    @git merge fresh

    @echo "[6/9] push updated main branch to the remote repo"
    @git push

    @echo "[7/9] switch do the fresh branch"
    @git checkout fresh

    @echo "[8/9] add the latest merge commit you did during the step 5 to the fresh branch, otherwise the history will be screwed in the next MRs"
    @git merge main

    @echo "[9/9] push changes of the fresh branch to the remote repo"
    @git push

    @echo "done"

# pull new upstream changes
update-upstream:
    @echo "updating upstream..."
    @cd ./upstream && git checkout master -q && git pull -q

# update VERSIONS.md file using the actual versions from roles' files
update-versions:
    @echo "generating versions diff..."
    @python bin/versions.py
    @python bin/versions.diff.py
    @python bin/commitmsg.py

# alias to match with the upstream recipes and docs
roles: pull-dependencies
