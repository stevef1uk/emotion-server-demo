#!/bin/bash
# Helper script to package GGUF model using secure_packager with customer public key and license token
# Ensures ONLY the holder of customer_private.pem can decrypt the model weights.
set -e

GGUF_DIR="${1:-/home/stevef/dev/my_udemy_stuff/latest_gemma3_project/gemma3_emotion_model_unsloth/gguf}"
OUT_DIR="${2:-/home/stevef/dev/my_udemy_stuff/latest_gemma3_project/gemma3_emotion_model_unsloth/release}"
KEYS_DIR="${3:-/home/stevef/dev/secure_packager/examples/example_docker/keys}"
PACKAGER_BIN="${4:-/home/stevef/dev/secure_packager/packager}"
ISSUE_TOKEN_BIN="${5:-/home/stevef/dev/secure_packager/issue-token}"

CUSTOMER_PUB="$KEYS_DIR/customer_public.pem"
VENDOR_PUB="$KEYS_DIR/vendor_public.pem"
VENDOR_PRIV="$KEYS_DIR/vendor_private.pem"

echo "=========================================================="
echo "Packaging Model with secure_packager"
echo "=========================================================="

if [ ! -d "$GGUF_DIR" ]; then
  echo "❌ Error: GGUF directory not found: $GGUF_DIR"
  exit 1
fi

if [ ! -f "$CUSTOMER_PUB" ] || [ ! -f "$VENDOR_PUB" ] || [ ! -f "$VENDOR_PRIV" ]; then
  echo "❌ Error: Required keys not found in $KEYS_DIR"
  echo "Expected: customer_public.pem, vendor_public.pem, vendor_private.pem"
  exit 1
fi

mkdir -p "$OUT_DIR"

echo "1. Encrypting model files with Fernet & wrapping with customer public key..."
"$PACKAGER_BIN" \
  -in "$GGUF_DIR" \
  -out "$OUT_DIR" \
  -pub "$CUSTOMER_PUB" \
  -vendor-pub "$VENDOR_PUB" \
  -license \
  -zip=true

echo "2. Issuing signed vendor license token..."
"$ISSUE_TOKEN_BIN" \
  -priv "$VENDOR_PRIV" \
  -expiry "2027-12-31" \
  -company "SJFisher Managed Service" \
  -email "sales@sjfisher.com" \
  -out "$OUT_DIR/token.txt"

echo "=========================================================="
echo "✅ Packaging complete!"
echo "Encrypted archive: $OUT_DIR/encrypted_files.zip"
echo "License token:     $OUT_DIR/token.txt"
echo "Decryptable ONLY with matching: $KEYS_DIR/customer_private.pem"
echo "=========================================================="
