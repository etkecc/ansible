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

# The decoys below live in the real defaults/main.yml too, and every one of
# them would be picked up by a looser match than the script uses: a commented
# out version, and another variable whose name ends in `_version` and which
# sorts before the real one would if the file were searched unanchored.
write_defaults() {
	local version="$1"

	cat > defaults/main.yml <<-EOF
		# livekit_server_version: v9.9.9

		livekit_server_container_image_self_build_repo_version: "{{ livekit_server_version }}"

		# renovate: datasource=docker depName=docker.io/livekit/livekit-server versioning=semver
		livekit_server_version: $version

		livekit_server_config_port: 7880
	EOF
}

# Starts a scenario with a repository at LiveKit Server v1.13.4 which has
# already seen two releases of it (v1.13.4-0 and v1.13.4-1).
scenario() {
	echo "$1"

	cleanup
	workdir="$(mktemp -d)"

	mkdir -p "$workdir/bin" "$workdir/defaults" "$workdir/tasks" "$workdir/templates" "$workdir/vars"
	cp "$script_under_test" "$workdir/bin/"
	cd "$workdir"

	git init -q -b main .
	git config user.email 'test@example.com'
	git config user.name 'Test'
	git config commit.gpgsign false

	write_defaults v1.13.4
	printf 'placeholder\n' > tasks/main.yml
	printf 'placeholder\n' > templates/env.j2
	printf 'placeholder\n' > vars/main.yml
	printf 'placeholder\n' > README.md
	mkdir -p molecule/default
	printf 'placeholder\n' > molecule/default/verify.yml

	git add -A
	git commit -qm 'Initial commit'

	local release_number
	for release_number in 0 1; do
		git tag "v1.13.4-$release_number"
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

bump_version='write_defaults v1.13.5'
revert_version='write_defaults v1.13.4'
edit_task="printf 'a task\n' >> tasks/main.yml"
edit_template="printf 'a line\n' >> templates/env.j2"
edit_vars="printf 'a derived variable\n' >> vars/main.yml"
edit_readme="printf 'documentation\n' >> README.md"
edit_molecule="printf 'an assertion\n' >> molecule/default/verify.yml"
edit_script="printf '# a comment\n' >> bin/compute-next-tag.sh"

# The two merge orders below apply the same updates and must each end up with
# every update released exactly once, whichever order they arrive in.

scenario 'A version bump merged before other role changes'
expect 'version bump' v1.13.5-0 "$(merge "$bump_version")"
expect 'task edit'    v1.13.5-1 "$(merge "$edit_task")"
expect 'template'     v1.13.5-2 "$(merge "$edit_template")"

scenario 'A version bump merged after other role changes'
expect 'task edit'    v1.13.4-2 "$(merge "$edit_task")"
expect 'version bump' v1.13.5-0 "$(merge "$bump_version")"

scenario 'Commits that do not affect the role'
expect 'README'   ''         "$(merge "$edit_readme")"
expect 'Molecule' ''         "$(merge "$edit_molecule")"
expect 'a script' ''         "$(merge "$edit_script")"
expect 'a task'   v1.13.4-2  "$(merge "$edit_task")"

# `vars/` holds the public URLs that playbooks consuming this role read, so a
# change there has to reach them.
scenario 'A change to vars/'
expect 'vars edit' v1.13.4-2 "$(merge "$edit_vars")"

scenario 'Release numbers past 9'
for release_number in 2 3 4 5 6 7 8 9 10; do
	git tag "v1.13.4-$release_number"
done
expect 'a task' v1.13.4-11 "$(merge "$edit_task")"

scenario 'Reverting to an already released version'
merge "$bump_version" > /dev/null
# The role is now identical to what v1.13.4-1 already published, so there is
# nothing new to release.
expect 'a revert' ''         "$(merge "$revert_version")"

scenario 'Reverting to an already released version, with a change'
merge "$bump_version" > /dev/null
expect 'a revert' v1.13.4-2  "$(merge "$revert_version && $edit_task")"

# A quoted value and a trailing comment are both shapes the version line has
# taken across the fleet, and neither may end up inside the tag.
scenario 'A quoted version with a trailing comment'
expect 'quoted' v1.13.5-0 "$(merge "printf 'livekit_server_version: \"v1.13.5\"  # pinned\n' > defaults/main.yml")"

if [ "$failures" -gt 0 ]; then
	echo >&2 "$failures scenario(s) behaved unexpectedly"
	exit 1
fi

echo 'All scenarios behaved as expected'
