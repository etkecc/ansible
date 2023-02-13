#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail
if [[ "${TRACE-0}" == "1" ]]; then
    set -o xtrace
fi

if [[ "${1-}" =~ ^-*h(elp)?$ ]]; then
    echo 'Usage: ./bin/versions.sh

Script will generate VERSIONS.md file based on component versions present in roles defaults/main.yml
'
    exit
fi

grep -rhE "^matrix_.*_version: |^custom_.*_version: |^int_.*_version: |^prometheus_.*_version: |^backup_.*_version: " ./upstream/roles/*/*/defaults/main.yml ./roles/*/*/defaults/main.yml | grep -Ev '{{|master|main|""' | sed -e "s/matrix_//;s/custom_//;s/int_//;s/_version//;/^synapse_default/d;/^synapse_ext/d;/^mailer_container/d;s/bot_//;s/client_//;s/mautrix_//" | sort | yq eval -M -P | sed "s/^/\*\ /" > $PWD/VERSIONS.md
