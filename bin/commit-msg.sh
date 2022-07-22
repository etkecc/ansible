#!/bin/sh

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

if [[ -z "$MESSAGE" ]]; then
	MESSAGE="update without version changes"
fi

echo $MESSAGE
