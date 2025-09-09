# Simple Go Dockerfile for Modal
FROM python:3.11-slim-bookworm

# Install Go
RUN apt-get update && apt-get install -y \
    golang-go \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages Modal needs
RUN pip install --no-cache-dir fastapi uvicorn requests

# Set working directory
WORKDIR /app

# Copy Go files
COPY main.go .
COPY go.mod .

# Build Go application
RUN go mod tidy && go build -o server main.go

# Make sure the binary is executable
RUN chmod +x server

# Expose port
EXPOSE 8000

# Default command (Modal will override this)
CMD ["./server"]
