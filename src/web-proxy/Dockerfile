# Ultra-lean Go Web Proxy Pod for Emotion Server
# Builds natively or cross-compiles for linux/arm64 (Raspberry Pi cluster)

FROM --platform=$BUILDPLATFORM golang:1.24-bookworm AS builder

ARG TARGETOS=linux
ARG TARGETARCH=arm64

WORKDIR /src

ENV CGO_ENABLED=0 \
    GOOS=${TARGETOS} \
    GOARCH=${TARGETARCH}

COPY go.mod ./
COPY . .

RUN go test -v ./... \
    && go build -ldflags="-s -w" -o /out/emotion-web .

FROM alpine:3.21

RUN apk add --no-cache ca-certificates tzdata curl \
    && addgroup -g 1000 app && adduser -D -u 1000 -G app app

WORKDIR /app
COPY --from=builder /out/emotion-web /app/emotion-web
RUN chown -R app:app /app

USER app
EXPOSE 8080

ENV PORT=8080 \
    GATEWAY_TOKEN_URL=https://preprod.agw.sjfisher.com/token \
    GATEWAY_MCP_URL=https://preprod.agw.sjfisher.com/mcp-emotion \
    TOKEN_TTL=900

HEALTHCHECK --interval=5s --timeout=3s --start-period=3s --retries=3 \
    CMD curl -f http://localhost:8080/healthz || exit 1

ENTRYPOINT ["/app/emotion-web"]
