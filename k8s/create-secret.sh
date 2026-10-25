#!/bin/bash
# Helper script to create the emotion-service-keys secret on k3s / Kubernetes
# Usage: ./create-secret.sh [path/to/customer_private.pem] [path/to/token.txt] [namespace]

set -e

KEY_FILE="${1:-./customer_private.pem}"
TOKEN_FILE="${2:-./token.txt}"
NAMESPACE="${3:-default}"

if [ ! -f "$KEY_FILE" ]; then
  echo "❌ Error: Customer private key not found at: $KEY_FILE"
  echo "Usage: $0 <path_to_customer_private.pem> <path_to_token.txt> [namespace]"
  exit 1
fi

if [ ! -f "$TOKEN_FILE" ]; then
  echo "❌ Error: License token not found at: $TOKEN_FILE"
  echo "Usage: $0 <path_to_customer_private.pem> <path_to_token.txt> [namespace]"
  exit 1
fi

echo "Creating Kubernetes secret 'emotion-service-keys' in namespace '$NAMESPACE'..."

kubectl create secret generic emotion-service-keys \
  --namespace="$NAMESPACE" \
  --from-file=customer_private.pem="$KEY_FILE" \
  --from-file=token.txt="$TOKEN_FILE" \
  --dry-run=client -o yaml | kubectl apply -f -

echo "✅ Secret 'emotion-service-keys' successfully created/updated in namespace '$NAMESPACE'!"
echo "You can now deploy the sidecar pod: kubectl apply -f emotion-mcp-sidecar.yaml -n $NAMESPACE"
