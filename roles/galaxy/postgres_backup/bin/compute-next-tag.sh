#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Slavi Pantaleev
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# Prints the tag that the currently checked out commit should be released as,
# or nothing at all if it does not warrant a release.
#
# Usage: bin/compute-next-tag.sh
#
# This role tracks one postgres-backup-local container image per supported
# Postgres major (`postgres_backup_container_image_v17`,
# `postgres_backup_container_image_v18`, ...). Only the newest supported major
# defines the tag, which looks like `v<newest Postgres major>-<release>`:
#
# - if defaults/main.yml gained support for a Postgres major that has never
#   been released, the release counter restarts at 0 (`v19-0`)
# - otherwise the counter is incremented (`v18-4`), but only if something that
#   actually affects the role has changed since the last release
#
# A change affecting an older major (say v17) therefore does not produce a
# misleading `v17-x` tag - it increments the newest major's counter, and the
# fix still reaches consumers through that release.
#
# Determining the version from defaults/main.yml, rather than from the commit
# message of the pull request that got merged, makes the result independent of
# the order in which pull requests get merged, and lets any change to the role
# (bugfix, feature, dependency bump) release itself without a human tagging.

set -euo pipefail

repository_path="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd -- "$repository_path"

defaults_path='defaults/main.yml'

# Paths that shape the behavior of the role for its consumers. A commit
# touching only other paths (a README fix, CI configuration, Molecule tests)
# does not change what a playbook run does, and releasing it would only create
# churn in the repositories that consume this role.
role_defining_paths=(
	'defaults'
	'meta'
	'tasks'
	'templates'
)

# The highest Postgres major that postgres_backup_container_image_v<N> covers.
# The values of these variables are container image references rather than
# version numbers, so it is the variable names that carry the version.
version="$(grep -E '^postgres_backup_container_image_v[0-9]+:' "$defaults_path" \
	| sed -E 's|^postgres_backup_container_image_v([0-9]+):.*$|\1|' \
	| sort -n | tail -n1)"

if [ -z "$version" ]; then
	echo >&2 "Could not determine the newest supported Postgres major from $defaults_path"
	exit 1
fi

tag_prefix="v${version}-"

# Of all releases of this version, the highest release number. Sorted
# numerically, so that -10 is recognized as newer than -9.
last_release="$(git tag --list "${tag_prefix}*" | sed -e "s|^${tag_prefix}||" | grep -E '^[0-9]+$' | sort -n | tail -n1 || true)"

if [ -z "$last_release" ]; then
	echo >&2 "Postgres $version has never been released"
	echo "${tag_prefix}0"
	exit 0
fi

previous_tag="${tag_prefix}${last_release}"

if git diff --quiet "$previous_tag" HEAD -- "${role_defining_paths[@]}"; then
	echo >&2 "Nothing affecting the role has changed since $previous_tag"
	exit 0
fi

echo >&2 "The role has changed since $previous_tag"
echo "${tag_prefix}$((last_release + 1))"
