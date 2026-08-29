#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Slavi Pantaleev
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# Prints the tag that the currently checked out commit should be released as,
# or nothing at all if it does not warrant a release.
#
# Usage: bin/compute-next-tag.sh
#
# Tags look like `v<version>-<release>`, which is what this repository has always
# published. It is at v1.0.0-7.
#
# This role is unusual among the roles of this fleet in that it deploys no
# software: it installs no container, has no upstream project and therefore no
# version of its own. It is a generic mechanism - a playbook hands it lists of
# directories, files, packages and commands, and it applies them to the host.
# `defaults/main.yml` holds nothing a version could be read out of, and Renovate
# has no leaf here to bump. The `1.0.0` in the tags is a number somebody picked
# by hand in 2023.
#
# So the version component is inherited from the newest tag that already exists
# and only the release counter moves. Should the role ever warrant a new series
# - a breaking change to its variables, say - tagging one commit by hand as
# `v2.0.0-0` is enough; everything after it continues from there.
#
# Either way the answer comes from the repository's state rather than from the
# commit message of whatever pull request got merged. That makes it independent
# of the order in which pull requests land, and lets any change to the role - a
# bugfix, a feature, a documentation fix in `defaults/main.yml` - release itself
# without a human tagging it. The workflow this replaced looked for a
# `renovate[bot]` commit whose subject mentioned "docker tag to"; because there
# is no Docker tag here for Renovate to bump, it had never once produced a tag,
# and every one of the eight releases this repository has was cut by hand.

set -euo pipefail

repository_path="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd -- "$repository_path"

# Paths that shape the behavior of the role for its consumers. A commit touching
# only other paths (a README fix, CI configuration, Molecule tests) does not
# change what a playbook run does, and releasing it would only create churn in
# the repositories that consume this role - mash-playbook, matrix-docker-ansible-deploy
# and etke.cc/ansible all pin it by tag.
#
# `files` and `templates` do not exist in this repository today. They are listed
# so that the day someone adds one, it counts as a change to the role rather
# than silently going unreleased.
role_defining_paths=(
	'defaults'
	'files'
	'meta'
	'tasks'
	'templates'
)

# Every tag this repository has ever published, newest last. The pattern is
# strict on purpose: only `v<numbers separated by dots>-<number>` counts, so a
# stray or hand-made tag cannot decide which series the next release belongs to.
released_tags="$(git tag --list 'v*' | grep -E '^v[0-9]+(\.[0-9]+)*-[0-9]+$' | sort -V || true)"

newest_tag="$(echo "$released_tags" | tail -n1)"

if [ -z "$newest_tag" ]; then
	echo >&2 'There is no previous tag to continue the release series from'
	exit 1
fi

tag_prefix="${newest_tag%-*}-"

# Of all releases in this series, the highest release number. Sorted numerically,
# so that -10 is recognized as newer than -9. The dots are escaped because the
# prefix is about to be used as a regular expression.
tag_prefix_pattern="${tag_prefix//./\\.}"
last_release="$(echo "$released_tags" | sed -ne "s|^${tag_prefix_pattern}||p" | grep -E '^[0-9]+$' | sort -n | tail -n1 || true)"

if [ -z "$last_release" ]; then
	echo >&2 "Version ${tag_prefix%-} has never been released"
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
