# Build stage
FROM golang:1.21-alpine AS builder

WORKDIR /app

# Copy go mod and sum files
COPY go.mod go.sum ./

# Download and verify dependencies
RUN go mod download && go mod verify

# Copy source code
COPY . .

# Build the MCP server (fix syntax errors during build)
RUN CGO_ENABLED=0 GOOS=linux go build -o mcp-emotion-server .

# Final stage
FROM alpine:latest

# Install nodejs and npm
RUN apk add --no-cache nodejs npm

# Create a non-root user
RUN adduser -D -u 1000 mcpuser

WORKDIR /app

# Copy the binary from builder
COPY --from=builder /app/mcp-emotion-server .

# Install supergateway globally
RUN npm install -g supergateway

# Set proper permissions
RUN chown -R mcpuser:mcpuser /app

# Switch to non-root user
USER mcpuser

# Expose port
EXPOSE 9000

# Environment variable for emotion service (can be overridden)
ENV EMOTION_SERVICE_URL=http://localhost:8000/predict

# Command to run the application with supergateway wrapping stdio MCP server
CMD ["npx", "-y", "supergateway", "--stdio", "/app/mcp-emotion-server", "--port", "9000", "--baseUrl", "http://0.0.0.0:9000", "--debug"]