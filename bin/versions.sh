#!/bin/sh
grep -rhE "^matrix_.*_version: |^custom_.*_version: |^int_.*_version: " ./upstream/roles/*/defaults/main.yml ./roles/*/*/defaults/main.yml | grep -Ev '{{|master|main|""' | sed -e "s/matrix_//;s/custom_//;s/int_//;s/_version//;/^synapse_default/d;/^synapse_ext/d;/^mailer_container/d;s/bot_//;s/client_//;s/mautrix_//" | sort | yq eval -M -P | sed "s/^/\*\ /" > $PWD/VERSIONS.md
