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

# The defaults file each scenario starts from. Besides the real version, it
# carries every neighbouring value that a careless reader of this file could
# pick up instead:
#
# - a commented-out version, sitting above the real one, which a pattern that
#   is not anchored to the start of the line would find first
# - a differently-prefixed variable whose name ends in the real one
# - the Jinja-derived image tag, which is what actually gets pulled but which
#   resolves to nothing outside of Ansible
#
# A script that keyed on any of them would produce v9.9.9-, v8.8.8- or an
# empty tag prefix rather than v1.10.0-.
write_defaults() {
	cat > defaults/main.yml <<-'DEFAULTS'
		# renovate: datasource=docker depName=ghcr.io/martin-helmich/prometheus-nginxlog-exporter/exporter versioning=semver
		# prometheus_nginxlog_exporter_version: v9.9.9
		prometheus_nginxlog_exporter_version: v1.10.0

		mash_prometheus_nginxlog_exporter_version: v8.8.8

		prometheus_nginxlog_exporter_container_image_tag: "{{ 'latest' if prometheus_nginxlog_exporter_version == 'master' else prometheus_nginxlog_exporter_version }}-{{ prometheus_nginxlog_exporter_architecture }}"
	DEFAULTS
}

# Starts a scenario with a repository at exporter 1.10.0 which has already
# seen two releases of it (v1.10.0-0 and v1.10.0-1).
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

	write_defaults
	printf 'placeholder\n' > tasks/main.yml
	printf 'placeholder\n' > templates/env.j2
	printf 'placeholder\n' > README.md

	git add -A
	git commit -qm 'Initial commit'

	local release_number
	for release_number in 0 1; do
		git tag "v1.10.0-$release_number"
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

bump_version="sed -i 's|^prometheus_nginxlog_exporter_version: v1.10.0|prometheus_nginxlog_exporter_version: v1.11.0|' defaults/main.yml"
revert_version="sed -i 's|^prometheus_nginxlog_exporter_version: v1.11.0|prometheus_nginxlog_exporter_version: v1.10.0|' defaults/main.yml"
edit_task="printf 'a task\n' >> tasks/main.yml"
edit_template="printf 'a line\n' >> templates/env.j2"
edit_readme="printf 'documentation\n' >> README.md"
edit_script="printf '# a comment\n' >> bin/compute-next-tag.sh"

# The two merge orders below apply the same updates and must each end up with
# every update released exactly once, whichever order they arrive in.

scenario 'A version bump merged before other role changes'
expect 'version bump' v1.11.0-0 "$(merge "$bump_version")"
expect 'task edit'    v1.11.0-1 "$(merge "$edit_task")"
expect 'template'     v1.11.0-2 "$(merge "$edit_template")"

scenario 'A version bump merged after other role changes'
expect 'task edit'    v1.10.0-2 "$(merge "$edit_task")"
expect 'version bump' v1.11.0-0 "$(merge "$bump_version")"

scenario 'Commits that do not affect the role'
expect 'README'   ''        "$(merge "$edit_readme")"
expect 'a script' ''        "$(merge "$edit_script")"
expect 'a task'   v1.10.0-2 "$(merge "$edit_task")"

scenario 'Release numbers past 9'
for release_number in 2 3 4 5 6 7 8 9 10; do
	git tag "v1.10.0-$release_number"
done
expect 'a task' v1.10.0-11 "$(merge "$edit_task")"

scenario 'Reverting to an already released version'
merge "$bump_version" > /dev/null
# The role is now identical to what v1.10.0-1 already published, so there is
# nothing new to release.
expect 'a revert' ''        "$(merge "$revert_version")"

scenario 'Reverting to an already released version, with a change'
merge "$bump_version" > /dev/null
expect 'a revert' v1.10.0-2 "$(merge "$revert_version && $edit_task")"

# The decoys in defaults/main.yml are present in every scenario above, so each
# of them already proves that none of them wins. This states it outright, so
# that a regression names itself rather than showing up as an off-by-one.
scenario 'Neighbouring values in defaults/main.yml are not mistaken for the version'
expect 'a task' v1.10.0-2 "$(merge "$edit_task")"
expect 'the commented-out version is ignored'  '' "$(git tag --list 'v9.9.9-*')"
expect 'the same-suffix variable is ignored'   '' "$(git tag --list 'v8.8.8-*')"

if [ "$failures" -gt 0 ]; then
	echo >&2 "$failures scenario(s) behaved unexpectedly"
	exit 1
fi

echo 'All scenarios behaved as expected'
