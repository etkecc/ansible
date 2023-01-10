CI_REGISTRY_IMAGE := env_var_or_default("CI_REGISTRY_IMAGE", "registry.gitlab.com/etke.cc/int/scheduler")
REGISTRY_IMAGE := env_var_or_default("REGISTRY_IMAGE", "registry.etke.cc/etke.cc/int/scheduler")
CI_COMMIT_TAG := if env_var_or_default("CI_COMMIT_TAG", "main") == "main" { "latest" } else { env_var_or_default("CI_COMMIT_TAG", "latest") }

# show help by default
default:
    @just --list --justfile {{ justfile() }}

# initialize upstream with pinned commit
submodules:
    git submodule update --init --recursive

# pull new upstream changes
upstream: && versions
    @cd ./upstream && git pull

# pull roles
roles:
    ansible-galaxy install -r requirements.yml -p roles/galaxy/ --force
    ansible-galaxy install -r upstream/requirements.yml -p roles/galaxy/ --force

# update VERSIONS.md file using the actual versions from roles' files
versions:
    bash bin/versions.sh
    git --no-pager diff --no-ext-diff VERSIONS.md

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
    python bin/feeds.py . dump

# dumps a file with list of hookshot commands with extracted git feeds for roles
hookshot:
    python bin/feeds.py . hookshot

# prints roles files for which a GIT feeds couldn't be extracted
nofeeds:
    python bin/feeds.py . check
