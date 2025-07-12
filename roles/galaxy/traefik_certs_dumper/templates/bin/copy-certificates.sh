#!/bin/sh

# SPDX-FileCopyrightText: 2023 Slavi Pantaleev
#
# SPDX-License-Identifier: AGPL-3.0-or-later

in=$1
staging=$2
out=$3

echo 'Copying traefik-certs-dumper certificates ('$in') to '$out' via '$staging

cp -ar $in/. $staging/.

chown -R {{ traefik_certs_dumper_dumped_certificates_dir_owner }}:{{ traefik_certs_dumper_dumped_certificates_dir_group }} $staging

rm -rf $out/*

mv $staging/* $out/.
