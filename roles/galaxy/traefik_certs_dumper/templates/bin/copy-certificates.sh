#!/bin/sh

# SPDX-FileCopyrightText: 2023 Slavi Pantaleev
#
# SPDX-License-Identifier: AGPL-3.0-or-later

if [ $# -ne 3 ] || [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
  echo "Usage: $0 <in_dir> <staging_dir> <out_dir>" >&2
  exit 1
fi

in=$1
staging=$2
out=$3

set -e

# traefik-certs-dumper runs post-hooks concurrently and without serialization
# (a single non-atomic acme.json write can trigger two hooks milliseconds apart).
# All invocations share $staging and $out, so they must not overlap.
# The lock is held on the staging directory itself, so no lock file ends up in $out.
exec 9<"$staging"
flock 9

echo "Copying traefik-certs-dumper certificates ($in) to $out via $staging"

rm -rf "$staging"/* "$staging"/.[!.]* "$staging"/..?*

cp -ar "$in/." "$staging/."

set -- "$staging"/*
if [ ! -e "$1" ] && [ ! -L "$1" ]; then
  echo "Nothing was dumped, keeping the existing certificates in $out"
  exit 0
fi

# The dumper may create an empty private/ directory even when there is no certificate data.
if [ -z "$(find "$@" -type f -print -quit)" ]; then
  echo "No certificate files were dumped, keeping the existing certificates in $out"
  exit 0
fi

chown -R {{ traefik_certs_dumper_dumped_certificates_dir_owner }}:{{ traefik_certs_dumper_dumped_certificates_dir_group }} "$staging"

rm -rf "$out"/*

mv "$@" "$out"/.
