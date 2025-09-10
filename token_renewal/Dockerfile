# Use the existing emotion service image as base
ARG BASE_IMAGE=stevef1uk/emotion-service:amd64
FROM ${BASE_IMAGE}

# Copy the new token file into the correct location with proper ownership
COPY --chown=65532:65532 --chmod=644 token.txt /app/gemma3_emotion_model_unsloth/release/token.txt
