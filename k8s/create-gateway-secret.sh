#!/usr/bin/env bash
# Create Kubernetes secret for Agent Gateway credentials without saving to disk.
# Usage:
#   ./create-gateway-secret.sh <delegation_id> <agent_secret>
# Or run with no arguments to be prompted securely.

set -euo pipefail

NAMESPACE="${KUBE_NAMESPACE:-default}"
SECRET_NAME="emotion-gateway-secret"

DELEGATION_ID="${1:-}"
AGENT_SECRET="${2:-}"

if [ -z "$DELEGATION_ID" ]; then
  read -rp "Enter Agent Gateway Delegation ID (e.g. del-xxxxxxxx...): " DELEGATION_ID
fi

if [ -z "$AGENT_SECRET" ]; then
  read -rsp "Enter Agent Gateway Agent Secret: " AGENT_SECRET
  echo
fi

if [ -z "$DELEGATION_ID" ] || [ -z "$AGENT_SECRET" ]; then
  echo "Error: both delegation_id and agent_secret are required." >&2
  exit 1
fi

echo "Creating or updating secret '${SECRET_NAME}' in namespace '${NAMESPACE}'..."
kubectl create secret generic "${SECRET_NAME}" \
  --namespace="${NAMESPACE}" \
  --from-literal=delegation-id="${DELEGATION_ID}" \
  --from-literal=agent-secret="${AGENT_SECRET}" \
  --dry-run=client -o yaml | kubectl apply -f -

echo "✓ Secret '${SECRET_NAME}' successfully configured."
