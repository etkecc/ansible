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

# Starts a scenario with a repository at Uptime Kuma 1.23.16 which has already
# seen two releases of it (v1.23.16-0 and v1.23.16-1).
#
# The defaults file reproduces the shape of the real one: the `# renovate:`
# annotation sits directly above the version, and the container image tag is
# derived from it. Both are there so that a script keying on the wrong line
# would be caught.
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

	{
		printf '# renovate: datasource=docker depName=louislam/uptime-kuma versioning=semver\n'
		printf 'uptime_kuma_version: 1.23.16\n'
		printf 'uptime_kuma_container_image_tag: "{{ uptime_kuma_version }}-alpine"\n'
		printf 'uptime_kuma_container_image: "{{ uptime_kuma_container_image_registry_prefix }}louislam/uptime-kuma:{{ uptime_kuma_container_image_tag }}"\n'
	} > defaults/main.yml

	printf 'placeholder\n' > tasks/main.yml
	printf 'placeholder\n' > templates/env.j2
	printf 'placeholder\n' > README.md

	git add -A
	git commit -qm 'Initial commit'

	local release_number
	for release_number in 0 1; do
		git tag "v1.23.16-$release_number"
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

bump_version="sed -i 's|^uptime_kuma_version: 1.23.16|uptime_kuma_version: 1.23.17|' defaults/main.yml"
revert_version="sed -i 's|^uptime_kuma_version: 1.23.17|uptime_kuma_version: 1.23.16|' defaults/main.yml"
edit_annotation="sed -i 's|versioning=semver|versioning=docker|' defaults/main.yml"
edit_image_flavor="sed -i 's|-alpine|-debian|' defaults/main.yml"
edit_task="printf 'a task\n' >> tasks/main.yml"
edit_template="printf 'a line\n' >> templates/env.j2"
edit_readme="printf 'documentation\n' >> README.md"
edit_script="printf '# a comment\n' >> bin/compute-next-tag.sh"

# The two merge orders below apply the same updates and must each end up with
# every update released exactly once, whichever order they arrive in.

scenario 'A version bump merged before other role changes'
expect 'version bump' v1.23.17-0 "$(merge "$bump_version")"
expect 'task edit'    v1.23.17-1 "$(merge "$edit_task")"
expect 'template'     v1.23.17-2 "$(merge "$edit_template")"

scenario 'A version bump merged after other role changes'
expect 'task edit'    v1.23.16-2 "$(merge "$edit_task")"
expect 'version bump' v1.23.17-0 "$(merge "$bump_version")"

scenario 'Commits that do not affect the role'
expect 'README'   ''         "$(merge "$edit_readme")"
expect 'a script' ''         "$(merge "$edit_script")"
expect 'a task'   v1.23.16-2 "$(merge "$edit_task")"

# Neither the annotation above the version nor the image tag derived from it is
# the version, so touching them must not be mistaken for a version bump. They
# do live in defaults/, so they still warrant a release of the current version.
scenario 'Lines around the version are not the version'
expect 'annotation'   v1.23.16-2 "$(merge "$edit_annotation")"
expect 'image flavor' v1.23.16-3 "$(merge "$edit_image_flavor")"

scenario 'Release numbers past 9'
for release_number in 2 3 4 5 6 7 8 9 10; do
	git tag "v1.23.16-$release_number"
done
expect 'a task' v1.23.16-11 "$(merge "$edit_task")"

scenario 'Reverting to an already released version'
merge "$bump_version" > /dev/null
# The role is now identical to what v1.23.16-1 already published, so there is
# nothing new to release.
expect 'a revert' ''         "$(merge "$revert_version")"

scenario 'Reverting to an already released version, with a change'
merge "$bump_version" > /dev/null
expect 'a revert' v1.23.16-2 "$(merge "$revert_version && $edit_task")"

if [ "$failures" -gt 0 ]; then
	echo >&2 "$failures scenario(s) behaved unexpectedly"
	exit 1
fi

echo 'All scenarios behaved as expected'
