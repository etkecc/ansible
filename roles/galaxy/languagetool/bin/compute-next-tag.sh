#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Slavi Pantaleev
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# Prints the tag that the currently checked out commit should be released as,
# or nothing at all if it does not warrant a release.
#
# Usage: bin/compute-next-tag.sh
#
# Tags look like `v<LanguageTool version>-<release>`:
#
# - if defaults/main.yml points at a LanguageTool version that has never been
#   released, the release counter restarts at 0 (`v6.8-0`)
# - otherwise the counter is incremented (`v6.8-1`), but only if something
#   that actually affects the role has changed since the last release
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
#
# This role has no `vars/` or `handlers/` directory; were one to be added, it
# would belong in this list.
role_defining_paths=(
	'defaults'
	'meta'
	'tasks'
	'templates'
)

version="$(sed -nE 's|^languagetool_version:[[:space:]]*"?([^"[:space:]]+)"?.*$|\1|p' "$defaults_path" | head -n1)"

if [ -z "$version" ]; then
	echo >&2 "Could not determine the LanguageTool version from $defaults_path"
	exit 1
fi

# The upstream image is tagged without a leading `v` (`6.8`), while the tags of
# this repository carry one (`v6.8-0`). Stripping a leading `v` that is not
# there today keeps the prefix correct should upstream ever add one.
#
# Upstream also publishes container-only rebuilds of an unchanged LanguageTool
# version as `6.7-dockerupdate-4`. Such a value is used verbatim here, giving
# tags like `v6.7-dockerupdate-4-0`, which keeps every distinct pinned image a
# distinct release series.
tag_prefix="v${version#v}-"

# Of all releases of this version, the highest release number. Sorted
# numerically, so that -10 is recognized as newer than -9.
#
# The `grep` is what keeps the series apart: with a `v6.7-` prefix, the tag
# `v6.7-dockerupdate-4-0` leaves `dockerupdate-4-0` behind, which is not a
# number and so is not mistaken for release 0 of plain `6.7`.
last_release="$(git tag --list "${tag_prefix}*" | sed -e "s|^${tag_prefix}||" | grep -E '^[0-9]+$' | sort -n | tail -n1 || true)"

if [ -z "$last_release" ]; then
	echo >&2 "Version $version has never been released"
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
