#!/usr/bin/env sh
set -eu

body=$(python3 -c 'import json, os; print(json.dumps({"msgtype": "m.text", "body": os.environ.get("CI_COMMIT_MESSAGE", "")}))')
curl -H "Content-Type: application/json" -H "Authorization: Bearer $MATRIX_TOKEN" "$MATRIX_URL_FRESH" -d "$body"
