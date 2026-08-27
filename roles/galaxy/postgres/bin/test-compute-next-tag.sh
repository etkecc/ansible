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

# Starts a scenario with a repository tracking Postgres 17.11 and 18.6, whose
# newest version has already seen two releases (v18.6-0 and v18.6-1).
scenario() {
	echo "$1"

	cleanup
	workdir="$(mktemp -d)"

	mkdir -p "$workdir/bin" "$workdir/defaults" "$workdir/tasks" "$workdir/vars"
	cp "$script_under_test" "$workdir/bin/"
	cd "$workdir"

	git init -q -b main .
	git config user.email 'test@example.com'
	git config user.name 'Test'
	git config commit.gpgsign false

	{
		printf 'postgres_container_image_v17_version: "17.11"\n'
		printf 'postgres_container_image_v18_version: "18.6"\n'
	} > defaults/main.yml
	printf 'placeholder\n' > tasks/main.yml
	printf 'placeholder\n' > vars/main.yml
	printf 'placeholder\n' > README.md

	git add -A
	git commit -qm 'Initial commit'

	local release_number
	for release_number in 0 1; do
		git tag "v18.6-$release_number"
	done
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

bump_newest="sed -i 's|18.6|18.7|' defaults/main.yml"
bump_older="sed -i 's|17.11|17.12|' defaults/main.yml"
add_v19='printf '"'"'postgres_container_image_v19_version: "19.0"\n'"'"' >> defaults/main.yml'
edit_task="printf 'a task\n' >> tasks/main.yml"
edit_vars="printf 'a var\n' >> vars/main.yml"
edit_readme="printf 'documentation\n' >> README.md"

scenario 'Bumps to the newest and to an older major, in either order'
expect 'older major (v17)'  v18.6-2 "$(merge "$bump_older")"
expect 'newest major (v18)' v18.7-0 "$(merge "$bump_newest")"

scenario 'Bumps to the newest and to an older major, the other way around'
expect 'newest major (v18)' v18.7-0 "$(merge "$bump_newest")"
expect 'older major (v17)'  v18.7-1 "$(merge "$bump_older")"

scenario 'A new major appears'
expect 'new major (v19)' v19.0-0 "$(merge "$add_v19")"
expect 'older major'     v19.0-1 "$(merge "$bump_older")"

scenario 'Commits that do not affect the role'
expect 'README' ''        "$(merge "$edit_readme")"
expect 'a task' v18.6-2   "$(merge "$edit_task")"
expect 'vars'   v18.6-3   "$(merge "$edit_vars")"

scenario 'Release numbers past 9'
for release_number in 2 3 4 5 6 7 8 9 10; do
	git tag "v18.6-$release_number"
done
expect 'a task' v18.6-11 "$(merge "$edit_task")"

if [ "$failures" -gt 0 ]; then
	echo >&2 "$failures scenario(s) behaved unexpectedly"
	exit 1
fi

echo 'All scenarios behaved as expected'
