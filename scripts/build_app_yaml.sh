#!/usr/bin/env bash
set -euo pipefail

BASE_FILE="${1:-app.yaml}"
CREDENTIALS_FILE="${2:-credentials.yaml}"
OUTPUT_FILE="${3:-app.deploy.yaml}"

if [[ ! -f "$BASE_FILE" ]]; then
  echo "Error: base file not found: $BASE_FILE" >&2
  exit 1
fi

if [[ ! -f "$CREDENTIALS_FILE" ]]; then
  echo "Error: credentials file not found: $CREDENTIALS_FILE" >&2
  echo "Tip: cp credentials.yaml.example credentials.yaml" >&2
  exit 1
fi

awk -v cred_file="$CREDENTIALS_FILE" '
  BEGIN { injected = 0 }
  {
    print $0
    if (!injected && $0 ~ /^env_variables:[[:space:]]*$/) {
      while ((getline line < cred_file) > 0) {
        if (line ~ /^[[:space:]]*#/ || line ~ /^[[:space:]]*$/) continue
        sub(/^[[:space:]]*/, "", line)
        print "  " line
      }
      close(cred_file)
      injected = 1
    }
  }
' "$BASE_FILE" > "$OUTPUT_FILE"

echo "Generated $OUTPUT_FILE from $BASE_FILE + $CREDENTIALS_FILE"
echo "Deploy with: gcloud app deploy $OUTPUT_FILE"