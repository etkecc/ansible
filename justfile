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
    #!/usr/bin/env bash
    set -euo pipefail
    if [ -x "$(command -v agru)" ]; then
        agru
    else
        ansible-galaxy install -r requirements.yml -p roles/galaxy/ --force
    fi

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

# Runs the playbook with the given list of arguments
run +extra_args:
    time ansible-playbook play/all.yml {{ extra_args }}

# Runs the playbook with the given list of comma-separated tags and optional arguments
run-tags tags *extra_args:
    just --justfile {{ justfile() }} run --tags={{ tags }} {{ extra_args }}
