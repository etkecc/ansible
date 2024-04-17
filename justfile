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

# Runs the playbook with the given list of arguments
run +extra_args:
    time ansible-playbook play/all.yml {{ extra_args }}

# Runs the playbook with the given list of comma-separated tags and optional arguments
run-tags tags *extra_args:
    just --justfile {{ justfile() }} run --tags={{ tags }} {{ extra_args }}

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
    set -euo pipefail
    if [ -x "$(command -v agru)" ]; then
        agru ${AGRU_CLEANUP:-}
    else
        ansible-galaxy install -r requirements.yml -p roles/galaxy/ --force
    fi

# pull all updates
update: update-self update-upstream && update-opml update-versions
    @agru -u

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

# merge fresh into master
update-stable:
    @echo "[1/9] force switch to the fresh branch"
    @git checkout fresh

    @echo "[2/9] fetch and apply any missing changes in the local fresh branch"
    @git pull

    @echo "[3/9] switch to the master branch"
    @git checkout master

    @echo "[4/9] fetch and apply any missing changes in the local master branch"
    @git pull

    @echo "[5/9] merge the fresh branch into the master branch"
    @git merge fresh

    @echo "[6/9] push updated master branch to the remote repo"
    @git push

    @echo "[7/9] switch do the fresh branch"
    @git checkout fresh

    @echo "[8/9] add the latest merge commit you did during the step 5 to the fresh branch, otherwise the history will be screwed in the next MRs"
    @git merge master

    @echo "[9/9] push changes of the fresh branch to the remote repo"
    @git push

    @echo "done"

# pull new upstream changes
update-upstream:
    @echo "updating upstream..."
    @cd ./upstream && git pull -q

# update VERSIONS.md file using the actual versions from roles' files
update-versions:
    @echo "generating versions diff..."
    @python bin/versions.py
    @python bin/commitmsg.py

# alias to match with the upstream recipes and docs
roles: pull-dependencies
