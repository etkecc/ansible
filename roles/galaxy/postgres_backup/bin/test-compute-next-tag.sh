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

# Starts a scenario with a repository supporting Postgres 17 and 18, whose
# newest major has already seen two releases (v18-0 and v18-1).
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
		printf 'postgres_backup_container_image_v9: "prodrigestivill/postgres-backup-local:9.6-{{ distro }}-2aa03d1"\n'
		printf 'postgres_backup_container_image_v17: "prodrigestivill/postgres-backup-local:17-{{ distro }}-234f538"\n'
		printf 'postgres_backup_container_image_v18: "prodrigestivill/postgres-backup-local:18-{{ distro }}-d257e5d"\n'
		printf 'postgres_backup_container_image_latest: "{{ postgres_backup_container_image_v18 }}"\n'
	} > defaults/main.yml
	printf 'placeholder\n' > tasks/main.yml
	printf 'placeholder\n' > templates/env.j2
	printf 'placeholder\n' > README.md

	git add -A
	git commit -qm 'Initial commit'

	local release_number
	for release_number in 0 1; do
		git tag "v18-$release_number"
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

bump_newest="sed -i 's|18-{{ distro }}-d257e5d|18-{{ distro }}-abc1234|' defaults/main.yml"
bump_older="sed -i 's|17-{{ distro }}-234f538|17-{{ distro }}-def5678|' defaults/main.yml"
add_v19='sed -i "s|^postgres_backup_container_image_latest:.*|postgres_backup_container_image_v19: \"prodrigestivill/postgres-backup-local:19-{{ distro }}-99aabbc\"\npostgres_backup_container_image_latest: \"{{ postgres_backup_container_image_v19 }}\"|" defaults/main.yml'
edit_task="printf 'a task\n' >> tasks/main.yml"
edit_template="printf 'a line\n' >> templates/env.j2"
edit_readme="printf 'documentation\n' >> README.md"

# The image references for a given major get new upstream builds without the
# major changing, so those bumps roll the counter rather than restarting it.
scenario 'Image bumps within the supported majors'
expect 'newest major (v18)' v18-2 "$(merge "$bump_newest")"
expect 'older major (v17)'  v18-3 "$(merge "$bump_older")"

scenario 'Image bumps within the supported majors, the other way around'
expect 'older major (v17)'  v18-2 "$(merge "$bump_older")"
expect 'newest major (v18)' v18-3 "$(merge "$bump_newest")"

scenario 'A new major appears'
expect 'new major (v19)' v19-0 "$(merge "$add_v19")"
expect 'older major'     v19-1 "$(merge "$bump_older")"

scenario 'Commits that do not affect the role'
expect 'README'     ''      "$(merge "$edit_readme")"
expect 'a task'     v18-2   "$(merge "$edit_task")"
expect 'a template' v18-3   "$(merge "$edit_template")"

# A double-digit major must not be mistaken for a single-digit one, and a
# release counter past 9 must sort numerically rather than lexically.
scenario 'Release numbers past 9'
for release_number in 2 3 4 5 6 7 8 9 10; do
	git tag "v18-$release_number"
done
expect 'a task' v18-11 "$(merge "$edit_task")"

if [ "$failures" -gt 0 ]; then
	echo >&2 "$failures scenario(s) behaved unexpectedly"
	exit 1
fi

echo 'All scenarios behaved as expected'
