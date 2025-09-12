# Use a base image that has both Python and Go
FROM python:3.11-slim

# Install Go and other dependencies
RUN apt-get update && \
    apt-get install -y wget && \
    wget https://go.dev/dl/go1.22.0.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go1.22.0.linux-amd64.tar.gz && \
    rm go1.22.0.linux-amd64.tar.gz && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set Go environment variables
ENV PATH="/usr/local/go/bin:${PATH}"
ENV GOPATH="/go"
ENV PATH="${GOPATH}/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy Go source code
COPY main.go .

# Build the Go binary
RUN CGO_ENABLED=0 GOOS=linux go build -o server main.go

# Install Python dependencies
RUN pip install flask requests

# Expose port
EXPOSE 8000

# Set the command to run the Go server
CMD ["./server"]
