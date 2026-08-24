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

# Starts a scenario with a repository that looks like this one: role files and
# no tags at all. Scenarios add whatever release history they need.
scenario() {
	echo "$1"

	cleanup
	workdir="$(mktemp -d)"

	mkdir -p "$workdir/bin" "$workdir/defaults" "$workdir/handlers" "$workdir/meta" "$workdir/tasks" "$workdir/templates"
	cp "$script_under_test" "$workdir/bin/"
	cd "$workdir"

	git init -q -b main .
	git config user.email 'test@example.com'
	git config user.name 'Test'
	git config commit.gpgsign false

	printf 'system_security_fail2ban_enabled: true\n' > defaults/main.yml
	printf 'placeholder\n' > handlers/main.yml
	printf 'galaxy_info:\n' > meta/main.yml
	printf 'placeholder\n' > tasks/main.yml
	printf 'placeholder\n' > templates/jail.local.j2
	printf 'placeholder\n' > README.md
	mkdir -p molecule/default
	printf 'placeholder\n' > molecule/default/verify.yml

	git add -A
	git commit -qm 'Initial commit'
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

edit_task="printf 'a task\n' >> tasks/main.yml"
edit_defaults="printf 'a_variable: true\n' >> defaults/main.yml"
edit_handler="printf 'a handler\n' >> handlers/main.yml"
edit_meta="printf '  role_name: fail2ban\n' >> meta/main.yml"
edit_template="printf 'a directive\n' >> templates/jail.local.j2"
edit_readme="printf 'documentation\n' >> README.md"
edit_molecule="printf 'an assertion\n' >> molecule/default/verify.yml"
edit_script="printf '# a comment\n' >> bin/compute-next-tag.sh"

scenario 'A repository with no releases yet'
expect 'a task edit' v1.0.0-0 "$(merge "$edit_task")"
expect 'another one' v1.0.0-1 "$(merge "$edit_task")"

scenario 'Every role-defining path triggers a release'
git tag v1.0.0-0
expect 'defaults'  v1.0.0-1 "$(merge "$edit_defaults")"
# fail2ban restarts through a handler, unlike most roles in this fleet, so
# handlers/ is role-defining here even though the shared script it was adapted
# from does not list it.
expect 'handlers'  v1.0.0-2 "$(merge "$edit_handler")"
expect 'meta'      v1.0.0-3 "$(merge "$edit_meta")"
expect 'tasks'     v1.0.0-4 "$(merge "$edit_task")"
expect 'templates' v1.0.0-5 "$(merge "$edit_template")"

scenario 'Commits that do not affect the role'
git tag v1.0.0-0
expect 'README'   '' "$(merge "$edit_readme")"
expect 'Molecule' '' "$(merge "$edit_molecule")"
expect 'a script' '' "$(merge "$edit_script")"
expect 'a task'   v1.0.0-1 "$(merge "$edit_task")"

# The state this repository is actually in when the workflow first runs: two
# releases behind, with role files that have changed since the newer one.
scenario 'The release history this repository already has'
git tag v1.0.0-0
git tag v1.0.0-1
expect 'a task' v1.0.0-2 "$(merge "$edit_task")"

scenario 'Release numbers past 9'
for release_number in 0 1 2 3 4 5 6 7 8 9 10; do
	git tag "v1.0.0-$release_number"
done
expect 'a task' v1.0.0-11 "$(merge "$edit_task")"

# The one lever a human has here: starting a new series by hand, because
# nothing about fail2ban itself can tell the script that the role's interface
# changed.
scenario 'A human starts a new series'
git tag v1.0.0-0
git tag v1.0.0-1
git tag v2.0.0-0
expect 'a task' v2.0.0-1 "$(merge "$edit_task")"

# The new series starts at -0 while the old one is at -12. Picking the newest
# tag by release number rather than by version would go back to v1.0.0-13.
scenario 'A new series whose counter is lower than the old one'
for release_number in 0 1 2 3 4 5 6 7 8 9 10 11 12; do
	git tag "v1.0.0-$release_number"
done
git tag v2.0.0-0
expect 'a task' v2.0.0-1 "$(merge "$edit_task")"

# Version sorting has to be version sorting: 1.10.0 is newer than 1.9.0, which
# a lexicographic sort gets backwards.
scenario 'Versions that sort differently as text'
git tag v1.9.0-0
git tag v1.10.0-0
expect 'a task' v1.10.0-1 "$(merge "$edit_task")"

# Tags that are not releases of this series must be ignored entirely, rather
# than being parsed into a nonsense version or release number.
scenario 'Tags that are not releases of this series'
git tag v1.0.0-0
git tag v1.0.0
git tag v9.9.9
git tag v1.0.0-rc1
git tag fail2ban-2.0.0-0
git tag latest
expect 'a task' v1.0.0-1 "$(merge "$edit_task")"

scenario 'A repository whose only tags are unparseable'
git tag latest
git tag stable
expect 'a task' v1.0.0-0 "$(merge "$edit_task")"

# A revert still differs from what the previous tag published, so it is a
# release of its own rather than a silent return to an older tag.
scenario 'Reverting a released change'
git tag v1.0.0-0
merge "$edit_task" > /dev/null
expect 'a revert' v1.0.0-2 "$(merge "sed -i '\$d' tasks/main.yml")"

if [ "$failures" -gt 0 ]; then
	echo >&2 "$failures scenario(s) behaved unexpectedly"
	exit 1
fi

echo 'All scenarios behaved as expected'
