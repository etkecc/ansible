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

echo "Copying traefik-certs-dumper certificates ($in) to $out via $staging"

cp -ar "$in/." "$staging/."

chown -R {{ traefik_certs_dumper_dumped_certificates_dir_owner }}:{{ traefik_certs_dumper_dumped_certificates_dir_group }} "$staging"

rm -rf "$out"/*

mv "$staging"/* "$out"/.
