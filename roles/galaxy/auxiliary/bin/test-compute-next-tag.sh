#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Slavi Pantaleev
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# Exercises bin/compute-next-tag.sh against throwaway git repositories.
#
# Usage: bin/test-compute-next-tag.sh
#
# Every scenario creates a repository in a temporary directory, gives it role
# files and a release history, and then replays a series of merges through the
# real script, tagging as it goes just like the autotag workflow does. This
# repository is never touched and no network access is needed.

set -euo pipefail

script_under_test="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/compute-next-tag.sh"

failures=0
workdir=''

cleanup() {
	cd /
	if [ -n "$workdir" ]; then
		rm -rf "$workdir"
		workdir=''
	fi
}

trap cleanup EXIT

# Starts a scenario with a repository in the state this one really is in: a
# `defaults/main.yml` that holds no version of any kind, and a release history.
#
# The defaults file deliberately carries the traps this role's real one has.
# Every value in it that a script looking for something version-shaped could
# latch onto is a permission mode or a user name, not a version:
# `aux_directory_default_mode: "0750"` would become `v0750-0` and
# `aux_file_default_mode: "0640"` would become `v0640-0`. Neither is a version
# of anything and the tag must not be derived from either.
scenario() {
	echo "$1"

	cleanup
	workdir="$(mktemp -d)"

	mkdir -p "$workdir/bin" "$workdir/defaults" "$workdir/files" "$workdir/meta" "$workdir/tasks" "$workdir/templates" "$workdir/molecule/default" "$workdir/.github/workflows"
	cp "$script_under_test" "$workdir/bin/"
	cd "$workdir"

	git init -q -b main .
	git config user.email 'test@example.com'
	git config user.name 'Test'
	git config commit.gpgsign false

	cat > defaults/main.yml <<-'YAML'
		aux_directory_default_mode: "0750"
		aux_directory_default_owner: root
		aux_directory_default_group: root
		aux_directory_definitions_custom: []
		aux_directory_definitions_auto: []
		aux_directory_definitions: "{{ aux_directory_definitions_auto + aux_directory_definitions_custom }}"
		aux_file_default_mode: "0640"
		aux_file_default_owner: root
		aux_file_default_group: root
		aux_file_definitions_custom: []
		aux_file_definitions_auto: []
		aux_file_definitions: "{{ aux_file_definitions_auto + aux_file_definitions_custom }}"
		aux_package_state: present
		aux_package_definitions_custom: []
		aux_command_default_become: false
		aux_command_default_become_user: root
		aux_command_default_ignore_errors: false
	YAML
	printf 'placeholder\n' > meta/main.yml
	printf 'placeholder\n' > tasks/main.yml
	printf 'placeholder\n' > README.md
	printf 'placeholder\n' > molecule/default/verify.yml
	printf 'placeholder\n' > .github/workflows/molecule.yml

	git add -A
	git commit -qm 'Initial commit'

	git tag v1.0.0-0
}

# Applies a change, commits it, and tags whatever the script says it should be.
# Prints the tag, or nothing when the script decided against a release.
merge() {
	local change="$1" tag

	eval "$change"
	git add -A
	git commit -qm 'Merge'

	tag="$(bin/compute-next-tag.sh 2>/dev/null)"

	if [ -n "$tag" ]; then
		git tag "$tag"
	fi

	printf '%s' "$tag"
}

expect() {
	local description="$1" expected="$2" actual="$3"

	if [ "$actual" = "$expected" ]; then
		printf '  ok   | %s -> %s\n' "$description" "${actual:-no release}"
	else
		printf '  FAIL | %s -> expected %s, got %s\n' "$description" "${expected:-no release}" "${actual:-no release}"
		failures=$((failures + 1))
	fi
}

edit_defaults="printf 'aux_extra_definitions: []\n' >> defaults/main.yml"
edit_task="printf 'a task\n' >> tasks/main.yml"
edit_meta="printf 'a line\n' >> meta/main.yml"
# Neither directory exists in the real repository yet. The script lists them
# anyway, so that adding one counts as a change to the role from day one.
edit_file="printf 'a line\n' >> files/some-file"
edit_template="printf 'a line\n' >> templates/some-template.j2"
edit_readme="printf 'documentation\n' >> README.md"
edit_workflow="printf '# a line\n' >> .github/workflows/molecule.yml"
edit_molecule="printf '# a line\n' >> molecule/default/verify.yml"
edit_script="printf '# a comment\n' >> bin/compute-next-tag.sh"

# Every change that affects the role has to be released exactly once, and the
# order in which the changes arrive must not matter.
scenario 'Changes to the role, released one after another'
expect 'defaults edit' v1.0.0-1 "$(merge "$edit_defaults")"
expect 'task edit'     v1.0.0-2 "$(merge "$edit_task")"
expect 'meta edit'     v1.0.0-3 "$(merge "$edit_meta")"
expect 'a new files/'     v1.0.0-4 "$(merge "$edit_file")"
expect 'a new templates/' v1.0.0-5 "$(merge "$edit_template")"

# Nothing in defaults/main.yml is a version, and a change to it must move the
# release counter rather than open a series named after some number found in it.
# A script grepping for something version-shaped would answer v0750-0 or
# v0640-0 here.
scenario 'A defaults change is a release, not a new series'
expect 'defaults edit' v1.0.0-1 "$(merge "$edit_defaults")"
expect 'defaults edit' v1.0.0-2 "$(merge "$edit_defaults")"

# The Molecule suite and the CI that runs it are the bulk of this repository's
# recent history and none of it changes what a playbook run does. Releasing it
# would push a new pin through mash-playbook, matrix-docker-ansible-deploy and
# etke.cc/ansible for no reason at all.
scenario 'Commits that do not affect the role'
expect 'README'          ''         "$(merge "$edit_readme")"
expect 'a workflow'      ''         "$(merge "$edit_workflow")"
expect 'a Molecule file' ''         "$(merge "$edit_molecule")"
expect 'a script'        ''         "$(merge "$edit_script")"
expect 'a task'          v1.0.0-1   "$(merge "$edit_task")"

# This repository is at v1.0.0-7 and heading for double digits, where a release
# number compared as a string would put -9 ahead of -10 and hand out a tag that
# already exists.
scenario 'Release numbers past 9'
for release_number in 1 2 3 4 5 6 7 8 9 10; do
	git tag "v1.0.0-$release_number"
done
expect 'a task' v1.0.0-11 "$(merge "$edit_task")"

# Older series exist and must not be continued from. If the newest tag were
# picked lexically rather than by version, the counter would carry on from
# v0.9.0-3, and if the release number were picked lexically, -10 would lose to -9.
scenario 'An older release series'
git tag v0.9.0-0
git tag v0.9.0-3
expect 'a task' v1.0.0-1 "$(merge "$edit_task")"

# Tags are compared as versions rather than as strings. Sorted as strings,
# `v10.0.0-0` would lose to `v9.0.0-0` and the series would run backwards.
scenario 'A double-digit major series'
git tag v9.0.0-0
git tag v10.0.0-0
expect 'a task' v10.0.0-1 "$(merge "$edit_task")"

# The same comparison one level down: a minor of 10 has to outrank a minor of 9.
scenario 'A double-digit minor series'
git tag v1.9.0-0
git tag v1.10.0-0
expect 'a task' v1.10.0-1 "$(merge "$edit_task")"

# The one manual step this scheme leaves: a breaking change to the role's
# variables is released by tagging it by hand, and everything after it continues
# from the new series.
scenario 'A new series opened by hand'
git tag v2.0.0-0
expect 'a task' v2.0.0-1 "$(merge "$edit_task")"
expect 'a task' v2.0.0-2 "$(merge "$edit_task")"

# Tags that are not releases of this role must not be mistaken for one. Picking
# up `v1.2` or `v1.0.0-rc1` would derail the series; `v3.0.0` without a release
# counter is not a release this scheme has ever published.
scenario 'Tags that are not releases'
git tag v1.2
git tag v1.0.0-rc1
git tag v3.0.0
git tag latest
expect 'a task' v1.0.0-1 "$(merge "$edit_task")"

# There is nothing to derive a version from other than the tags themselves, so a
# repository without any must refuse to answer rather than invent a series.
scenario 'No release history at all'
git tag -d v1.0.0-0 > /dev/null
printf 'a task\n' >> tasks/main.yml
git add -A
git commit -qm 'Merge'
if bin/compute-next-tag.sh > /dev/null 2>&1; then
	printf '  FAIL | no tags -> expected a refusal, got a success\n'
	failures=$((failures + 1))
else
	printf '  ok   | no tags -> refused\n'
fi

if [ "$failures" -gt 0 ]; then
	echo >&2 "$failures scenario(s) behaved unexpectedly"
	exit 1
fi

echo 'All scenarios behaved as expected'
