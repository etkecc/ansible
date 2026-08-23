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

# The fixture mirrors the shape of the real defaults/main.yml rather than just
# the one line the script cares about. Funkwhale runs as several processes off
# a pair of images, and each of them carries its own `*_version` variable
# defined in terms of `funkwhale_version`. Those decoys sit both before and
# after the real definition here, so a script that matched `_version:` loosely,
# or took the first or last match instead of the anchored one, would fail these
# scenarios by reading `{{ funkwhale_version }}` as if it were a version number.
write_defaults() {
	local version="$1"

	cat > defaults/main.yml <<-EOF
		funkwhale_identifier: funkwhale
		funkwhale_api_version: "{{ funkwhale_version }}"
		funkwhale_frontend_version: "{{ funkwhale_version }}"

		# renovate: datasource=docker depName=funkwhale/api versioning=semver
		funkwhale_version: $version

		funkwhale_celery_beat_version: "{{ funkwhale_version }}"
		funkwhale_celery_worker_version: "{{ funkwhale_version }}"
		funkwhale_watch_imports_version: "{{ funkwhale_version }}"
	EOF
}

# Starts a scenario with a repository at Funkwhale 1.4.1 which has already
# seen two releases of it (v1.4.1-0 and v1.4.1-1).
scenario() {
	echo "$1"

	cleanup
	workdir="$(mktemp -d)"

	mkdir -p "$workdir/bin" "$workdir/defaults" "$workdir/meta" "$workdir/tasks" "$workdir/templates"
	cp "$script_under_test" "$workdir/bin/"
	cd "$workdir"

	git init -q -b main .
	git config user.email 'test@example.com'
	git config user.name 'Test'
	git config commit.gpgsign false

	write_defaults 1.4.1
	printf 'placeholder\n' > meta/main.yml
	printf 'placeholder\n' > tasks/main.yml
	printf 'placeholder\n' > templates/env_api.j2
	printf 'placeholder\n' > README.md
	mkdir -p molecule/default
	printf 'placeholder\n' > molecule/default/verify.yml

	git add -A
	git commit -qm 'Initial commit'

	local release_number
	for release_number in 0 1; do
		git tag "v1.4.1-$release_number"
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

bump_version='write_defaults 1.4.2'
bump_major='write_defaults 2.0.9'
revert_version='write_defaults 1.4.1'
edit_task="printf 'a task\n' >> tasks/main.yml"
edit_template="printf 'a line\n' >> templates/env_api.j2"
edit_meta="printf 'a line\n' >> meta/main.yml"
edit_readme="printf 'documentation\n' >> README.md"
edit_molecule="printf 'a probe\n' >> molecule/default/verify.yml"
edit_script="printf '# a comment\n' >> bin/compute-next-tag.sh"

# The two merge orders below apply the same updates and must each end up with
# every update released exactly once, whichever order they arrive in.

scenario 'A version bump merged before other role changes'
expect 'version bump' v1.4.2-0 "$(merge "$bump_version")"
expect 'task edit'    v1.4.2-1 "$(merge "$edit_task")"
expect 'template'     v1.4.2-2 "$(merge "$edit_template")"

scenario 'A version bump merged after other role changes'
expect 'task edit'    v1.4.1-2 "$(merge "$edit_task")"
expect 'version bump' v1.4.2-0 "$(merge "$bump_version")"

scenario 'A major version bump'
expect 'major bump' v2.0.9-0 "$(merge "$bump_major")"
expect 'meta edit'  v2.0.9-1 "$(merge "$edit_meta")"

scenario 'Commits that do not affect the role'
expect 'README'    ''        "$(merge "$edit_readme")"
expect 'a script'  ''        "$(merge "$edit_script")"
expect 'a Molecule probe' '' "$(merge "$edit_molecule")"
expect 'a task'    v1.4.1-2  "$(merge "$edit_task")"

scenario 'Release numbers past 9'
for release_number in 2 3 4 5 6 7 8 9 10; do
	git tag "v1.4.1-$release_number"
done
expect 'a task' v1.4.1-11 "$(merge "$edit_task")"

scenario 'Reverting to an already released version'
merge "$bump_version" > /dev/null
# The role is now identical to what v1.4.1-1 already published, so there is
# nothing new to release.
expect 'a revert' '' "$(merge "$revert_version")"

scenario 'Reverting to an already released version, with a change'
merge "$bump_version" > /dev/null
expect 'a revert' v1.4.1-2 "$(merge "$revert_version && $edit_task")"

if [ "$failures" -gt 0 ]; then
	echo >&2 "$failures scenario(s) behaved unexpectedly"
	exit 1
fi

echo 'All scenarios behaved as expected'
