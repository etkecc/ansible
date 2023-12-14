#!/usr/bin/env sh

curl -H "Content-Type: application/json" -H "Authorization: Bearer $MATRIX_TOKEN" $MATRIX_URL_FRESH -d "{\"msgtype\":\"m.text\", \"body":\"$CI_COMMIT_MESSAGE\"}"
