# Multi-arch MCP Emotion Server
# Builds natively for linux/amd64 and linux/arm64 using BuildKit cross-compilation

FROM --platform=$BUILDPLATFORM golang:1.24-bookworm AS builder

# TARGETOS and TARGETARCH are automatically supplied by docker buildx
ARG TARGETOS
ARG TARGETARCH

WORKDIR /src

# Configure cross-compilation environment
ENV CGO_ENABLED=0 \
    GOOS=${TARGETOS} \
    GOARCH=${TARGETARCH}

COPY go.mod go.sum ./
RUN GOPROXY="${GOPROXY:-https://proxy.golang.org,direct}" go mod download

COPY . .

RUN go vet ./... \
    && go test ./... \
    && go build -ldflags="-s -w" -o /out/mcp-emotion-server .

# Minimal, secure runtime stage
FROM alpine:3.21

RUN apk add --no-cache ca-certificates tzdata curl \
    && addgroup -g 1000 app && adduser -D -u 1000 -G app app

WORKDIR /app
COPY --from=builder /out/mcp-emotion-server /app/mcp-emotion-server
RUN chown -R app:app /app

USER app
EXPOSE 9000

ENV MCP_HOST=0.0.0.0 \
    MCP_PORT=9000 \
    MCP_TRANSPORT=dual \
    EMOTION_SERVICE_URL=http://emotion-api:8000/predict

HEALTHCHECK --interval=5s --timeout=3s --start-period=3s --retries=5 \
    CMD curl -f http://localhost:9000/health || exit 1

ENTRYPOINT ["/app/mcp-emotion-server"]
