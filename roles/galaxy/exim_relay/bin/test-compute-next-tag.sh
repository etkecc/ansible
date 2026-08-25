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

# Starts a scenario with a repository at exim-relay 4.99.1-r0-2 which has
# already seen two releases of it (v4.99.1-r0-2-0 and v4.99.1-r0-2-1).
scenario() {
	echo "$1"

	cleanup
	workdir="$(mktemp -d)"

	mkdir -p "$workdir/bin" "$workdir/defaults" "$workdir/tasks" "$workdir/templates"
	cp "$script_under_test" "$workdir/bin/"
	cd "$workdir"

	git init -q -b main .
	git config user.email 'test@example.com'
	git config user.name 'Test'
	git config commit.gpgsign false

	printf 'exim_relay_version: 4.99.1-r0-2\n' > defaults/main.yml
	printf 'placeholder\n' > tasks/main.yml
	printf 'placeholder\n' > templates/env.j2
	printf 'placeholder\n' > README.md

	git add -A
	git commit -qm 'Initial commit'

	local release_number
	for release_number in 0 1; do
		git tag "v4.99.1-r0-2-$release_number"
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

# An image rebuild of the same Exim release, which is what most bumps here are.
bump_image_revision="sed -i 's|exim_relay_version: 4.99.1-r0-2|exim_relay_version: 4.99.1-r0-3|' defaults/main.yml"
revert_image_revision="sed -i 's|exim_relay_version: 4.99.1-r0-3|exim_relay_version: 4.99.1-r0-2|' defaults/main.yml"
# A new upstream Exim release.
bump_exim="sed -i 's|exim_relay_version: 4.99.1-r0-2|exim_relay_version: 4.100-r0-0|' defaults/main.yml"
prefix_version="sed -i 's|exim_relay_version: 4.99.1-r0-2|exim_relay_version: v4.99.1-r0-3|' defaults/main.yml"
edit_task="printf 'a task\n' >> tasks/main.yml"
edit_template="printf 'a line\n' >> templates/env.j2"
edit_readme="printf 'documentation\n' >> README.md"
edit_script="printf '# a comment\n' >> bin/compute-next-tag.sh"

# The two merge orders below apply the same updates and must each end up with
# every update released exactly once, whichever order they arrive in.

scenario 'A version bump merged before other role changes'
expect 'version bump' v4.99.1-r0-3-0 "$(merge "$bump_image_revision")"
expect 'task edit'    v4.99.1-r0-3-1 "$(merge "$edit_task")"
expect 'template'     v4.99.1-r0-3-2 "$(merge "$edit_template")"

scenario 'A version bump merged after other role changes'
expect 'task edit'    v4.99.1-r0-2-2 "$(merge "$edit_task")"
expect 'version bump' v4.99.1-r0-3-0 "$(merge "$bump_image_revision")"

scenario 'A new upstream Exim release'
expect 'Exim bump' v4.100-r0-0-0 "$(merge "$bump_exim")"
expect 'task edit' v4.100-r0-0-1 "$(merge "$edit_task")"

scenario 'Commits that do not affect the role'
expect 'README'   ''              "$(merge "$edit_readme")"
expect 'a script' ''              "$(merge "$edit_script")"
expect 'a task'   v4.99.1-r0-2-2  "$(merge "$edit_task")"

scenario 'Release numbers past 9'
for release_number in 2 3 4 5 6 7 8 9 10; do
	git tag "v4.99.1-r0-2-$release_number"
done
expect 'a task' v4.99.1-r0-2-11 "$(merge "$edit_task")"

# The version string contains dashes of its own, so a neighboring image
# revision must not be read as a release number of the current one.
scenario 'Tags of a neighboring image revision'
git tag 'v4.99.1-r0-20-0'
git tag 'v4.99.1-r0-20-1'
expect 'a task' v4.99.1-r0-2-2 "$(merge "$edit_task")"

# Likewise, the release history of an older Exim release, whose tags share a
# prefix with a shorter version value, must not be read as this one's.
scenario 'Tags of an older Exim release sharing a prefix'
git tag 'v4.99.1-r0-2-0-legacy'
expect 'a task' v4.99.1-r0-2-2 "$(merge "$edit_task")"

scenario 'Reverting to an already released version'
merge "$bump_image_revision" > /dev/null
# The role is now identical to what v4.99.1-r0-2-1 already published, so there
# is nothing new to release.
expect 'a revert' '' "$(merge "$revert_image_revision")"

scenario 'Reverting to an already released version, with a change'
merge "$bump_image_revision" > /dev/null
expect 'a revert' v4.99.1-r0-2-2 "$(merge "$revert_image_revision && $edit_task")"

scenario 'A version value carrying a leading v does not double it in the tag'
expect 'version bump' v4.99.1-r0-3-0 "$(merge "$prefix_version")"

if [ "$failures" -gt 0 ]; then
	echo >&2 "$failures scenario(s) behaved unexpectedly"
	exit 1
fi

echo 'All scenarios behaved as expected'
