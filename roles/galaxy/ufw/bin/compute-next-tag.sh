#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Slavi Pantaleev
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# Prints the tag that the currently checked out commit should be released as,
# or nothing at all if it does not warrant a release.
#
# Usage: bin/compute-next-tag.sh
#
# ---------------------------------------------------------------------------
# ufw has no version this role can key releases on - read this before
# changing anything here
# ---------------------------------------------------------------------------
#
# Every other role in the fleet names its tags after the version of the
# software it installs, read out of defaults/main.yml. This role cannot: it
# installs no container image and pins no version. It runs
# `ansible.builtin.package: name=ufw state=present`, so the version that ends
# up on a server is whatever the distribution's package repository offers that
# day - a different one on Debian 13 than on Ubuntu 26.04, changing under the
# role without a single commit here. There is no variable to read, and putting
# a number in defaults/main.yml just to have something to read would be a
# fiction that nothing enforces.
#
# So the version half of the tag is not derived from anything. It is a
# statement about this role's own interface - its variables and their meaning -
# and only a human can decide when that changed. The tags this repository has
# always used encode exactly that: a single `v1.0.0-0`, with the release
# counter carrying all of the information.
#
# This script therefore automates only the half that can be automated. It
# takes the version from the newest tag that already exists and increments the
# counter. Starting a new series stays a human act: tagging `v2.0.0-0` by hand
# (say, when a variable is renamed) is enough, and every release after it
# follows along as `v2.0.0-1`, `v2.0.0-2`, ... with no change to this file.
#
# ---------------------------------------------------------------------------
#
# Tags look like `v<version>-<release>`:
#
# - with no tags at all, the first release is `v1.0.0-0`
# - otherwise the counter of the newest version is incremented (`v1.0.0-1`),
#   but only if something that actually affects the role has changed since
#   that release
#
# Deriving the release from what the commit changed, rather than from the
# commit message of the pull request that got merged, makes the result
# independent of the order in which pull requests get merged, and lets any
# change to the role (bugfix, feature, dependency bump) release itself without
# a human tagging.

set -euo pipefail

repository_path="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd -- "$repository_path"

# The version to start with when this repository has no releases yet.
initial_version='1.0.0'

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

# The newest version any tag names. Only tags of the exact `vX.Y.Z-N` shape
# are considered, so that a stray `v1.0.0`, a `v1.0.0-rc1` or a tag with some
# other naming scheme entirely cannot be mistaken for a release of this
# series. Sorted with `sort -V`, so that 1.10.0 is recognized as newer
# than 1.9.0.
version="$(
	git tag --list 'v*-*' \
		| sed -nE 's|^v([0-9]+\.[0-9]+\.[0-9]+)-[0-9]+$|\1|p' \
		| sort -uV \
		| tail -n1
)"

if [ -z "$version" ]; then
	version="$initial_version"
fi

tag_prefix="v${version}-"

# Of all releases of this version, the highest release number. Sorted
# numerically, so that -10 is recognized as newer than -9.
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
