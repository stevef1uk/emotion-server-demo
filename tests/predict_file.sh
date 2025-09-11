#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat <<'EOF'
Usage: predict_file.sh [-u URL] FILE

Send the contents of FILE to the Emotion API as JSON {"text": "..."}.

Options:
  -u URL   Override endpoint URL (default: http://localhost:8000/predict)
  -h       Show this help

Notes:
  - Uses jq -Rs to safely JSON-escape all characters from FILE.
  - Prints the API response prettified via jq if available; raw otherwise.
EOF
}

ENDPOINT="http://localhost:8000/predict"

while getopts ":u:h" opt; do
  case "$opt" in
    u)
      ENDPOINT="$OPTARG"
      ;;
    h)
      usage
      exit 0
      ;;
    :)
      echo "Error: Option -$OPTARG requires an argument" >&2
      usage
      exit 2
      ;;
    *)
      echo "Error: Invalid option -$OPTARG" >&2
      usage
      exit 2
      ;;
  esac
done
shift $((OPTIND-1))

if [ $# -ne 1 ]; then
  echo "Error: Missing FILE argument" >&2
  usage
  exit 2
fi

FILE_PATH="$1"

if [ ! -f "$FILE_PATH" ]; then
  echo "Error: FILE not found: $FILE_PATH" >&2
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "Error: jq is required but not found in PATH" >&2
  exit 1
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "Error: curl is required but not found in PATH" >&2
  exit 1
fi

# Build JSON payload safely: {"text": <file contents as a single string>}
payload=$(jq -Rs '{text:.}' < "$FILE_PATH")
echo "$payload" 

# Send request
response=$(curl -s -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  -d "$payload")

# Pretty print if possible
if command -v jq >/dev/null 2>&1; then
  echo "$response" | jq .
else
  echo "$response"
fi


