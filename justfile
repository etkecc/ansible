# show help by default
default:
    @just --list --justfile {{ justfile() }}

# initialize upstream with pinned commit
submodules:
    git submodule update --init --recursive

# pull new upstream changes
upstream:
    @echo "updating upstream..."
    @cd ./upstream && git pull -q

# pull roles
roles:
    #!/usr/bin/env sh
    set -euo pipefail
    if [ -x "$(command -v agru)" ]; then
        agru ${AGRU_CLEANUP:-}
    else
        ansible-galaxy install -r requirements.yml -p roles/galaxy/ --force
    fi

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

# pull dependencies
dependencies: submodules roles

# pull all updates
update: upstream && opml hookshot versions
    @agru -u

# update VERSIONS.md file using the actual versions from roles' files
versions:
    @echo "generating versions diff..."
    @bash bin/versions.sh
    @git --no-pager diff --no-ext-diff VERSIONS.md

# run ansible-lint
lint:
    ansible-lint --project-dir . --exclude upstream

# make commit
commit: opml hookshot versions
    @git add --all
    @git commit -S -q -m "`bash bin/commit-msg.sh`"
    @echo "Changes have been committed"

# dumps an OPML file with extracted git feeds for roles
opml:
    @echo "generating opml..."
    @python bin/feeds.py . dump

# dumps a file with list of hookshot commands with extracted git feeds for roles
hookshot:
    @echo "generating hookshot..."
    @python bin/feeds.py . hookshot

# prints roles files for which a GIT feeds couldn't be extracted
nofeeds:
    python bin/feeds.py . check

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
