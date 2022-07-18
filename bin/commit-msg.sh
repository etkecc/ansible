#!/bin/sh
grep -rhE "^matrix_.*_version: |^custom_.*_version: |^int_.*_version: " ./upstream/roles/*/defaults/main.yml ./roles/*/*/defaults/main.yml | grep -Ev '{{|master|main|""' | sed -e "s/matrix_//;s/custom_//;s/int_//;s/_version//;/^synapse_default/d;/^synapse_ext/d;/^mailer_container/d;s/bot_//;s/client_//;s/mautrix_//" | sort | yq eval -M -P | sed "s/^/\*\ /" > $PWD/VERSIONS.md

PREFIX_OLD="\-\*"
PREFIX_NEW="\+\*"
CHANGE_SYMBOL="->"
DIFF=$(git diff --no-ext-diff VERSIONS.md)
declare -A CHANGES

while IFS= read -r LINE; do
	if [[ "$LINE" =~ ^$PREFIX_OLD.* ]]; then
		IFS=" " read -ra lineparts <<< "$LINE"
		item=$(echo "${lineparts[1],,}" | sed -e 's/://g')
		version="${lineparts[2],,}"
		CHANGES["$item"]="${version} ${CHANGE_SYMBOL} "
	fi

	if [[ "$LINE" =~ ^$PREFIX_NEW.* ]]; then
		IFS=" " read -ra lineparts <<< "$LINE"
		item=$(echo "${lineparts[1],,}" | sed -e 's/://g')
		version="${lineparts[2],,}"
		CHANGES["$item"]="${CHANGES[${item}]}${version}"
	fi
done <<< "$DIFF"

MESSAGE=""
for item in "${!CHANGES[@]}"; do
	change="${CHANGES[$item]}"
	if [[ -z "${change##*$CHANGE_SYMBOL*}" ]]; then
		MESSAGE="${MESSAGE} update ${item} (${change});"
	else
		MESSAGE="${MESSAGE} add ${item} (${change});"
	fi
done

echo $MESSAGE
