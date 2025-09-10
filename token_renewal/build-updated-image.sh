#!/bin/bash

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOKEN_FILE="token.txt"
IMAGE_TAG="emotion-service-updated:latest"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[BUILD]${NC} $1"
}

# Function to detect platform and set base image
detect_platform() {
    local arch=$(uname -m)
    local os=$(uname -s)
    
    case "$arch" in
        x86_64)
            echo "stevef1uk/emotion-service:amd64"
            ;;
        arm64|aarch64)
            if [ "$os" = "Darwin" ]; then
                echo "stevef1uk/emotion-service:arm64"  # Mac M1/M2
            else
                echo "stevef1uk/emotion-server:arm"     # ARM64 Linux/RPi
            fi
            ;;
        armv7l|armv6l)
            echo "stevef1uk/emotion-server:arm"         # RPi 32-bit
            ;;
        *)
            print_error "Unknown architecture: $arch"
            echo "stevef1uk/emotion-service:amd64"
            ;;
    esac
}

# Corrected function to display license details from the colon-separated token
display_license_info() {
    local token_file="$1"
    
    if [ ! -f "$token_file" ]; then
        print_error "License token file not found: $token_file"
        return 1
    fi
    
    print_status "📄 Decoding and displaying license information..."
    
    # Read the token, then base64 decode it
    local decoded_token
    decoded_token=$(cat "$token_file" | base64 -d 2>/dev/null)
    
    if [ -z "$decoded_token" ]; then
        print_error "Failed to decode license token. Is it a valid base64-encoded token?"
        return 1
    fi
    
    # Parse the colon-separated fields
    local expiry=$(echo "$decoded_token" | cut -d':' -f1)
    local company=$(echo "$decoded_token" | cut -d':' -f2)
    local email=$(echo "$decoded_token" | cut -d':' -f3)
    
    echo -e "${YELLOW}📄 License Information:${NC}"
    echo -e "${YELLOW}   Company: ${NC}${company}"
    echo -e "${YELLOW}   Email: ${NC}${email}"
    echo -e "${YELLOW}   Expires: ${NC}${expiry}"
    echo
}


main() {
    print_header "Building Updated Emotion Service Image"
    echo
    
    # Check if Docker is available
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed."
        exit 1
    fi
    
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker."
        exit 1
    fi
    
    # Check for token file
    if [ "$#" -eq 1 ] && [ -f "$1" ]; then
        TOKEN_SOURCE="$1"
    elif [ -f "$TOKEN_FILE" ]; then
        TOKEN_SOURCE="$TOKEN_FILE"
    else
        print_error "Token file not found!"
        echo "Usage: $0 [path_to_token.txt]"
        echo "  OR: Place 'token.txt' in the current directory"
        exit 1
    fi
    
    # Copy token file to expected name if needed
    if [ "$TOKEN_SOURCE" != "$TOKEN_FILE" ]; then
        print_status "Copying token file..."
        cp "$TOKEN_SOURCE" "$TOKEN_FILE"
    fi
    
    # Detect platform
    BASE_IMAGE=$(detect_platform)
    print_status "Using base image: $BASE_IMAGE"
    
    # Build new image
    print_status "Building updated image with new token..."
    if docker build \
        --build-arg BASE_IMAGE="$BASE_IMAGE" \
        -t "$IMAGE_TAG" \
        -f Dockerfile \
        .; then
        
        echo
        print_status "✅ Image built successfully: $IMAGE_TAG"
        
        # Call the new function to display the license info
        display_license_info "$TOKEN_SOURCE"
        
        # Stop existing container if running
        print_status "Checking for existing containers..."
        
        # Check for any containers using port 8000
        PORT_USERS=$(docker ps --format "table {{.Names}}\t{{.Ports}}" | grep ":8000->" | awk '{print $1}' || true)
        if [ ! -z "$PORT_USERS" ]; then
            print_status "Found containers using port 8000: $PORT_USERS"
            for container in $PORT_USERS; do
                print_status "Stopping container: $container"
                docker stop "$container" >/dev/null 2>&1 || true
                docker rm "$container" >/dev/null 2>&1 || true
            done
        fi
        
        # Also check specifically for emotion-service containers
        EMOTION_CONTAINERS=$(docker ps -aq -f name=emotion-service || true)
        if [ ! -z "$EMOTION_CONTAINERS" ]; then
            print_status "Cleaning up emotion-service containers..."
            docker stop $EMOTION_CONTAINERS >/dev/null 2>&1 || true
            docker rm $EMOTION_CONTAINERS >/dev/null 2>&1 || true
        fi
        
        # Wait a moment for port to be released
        sleep 2
        
        # Run new container
        print_status "Starting container with updated token..."
        if docker run -d \
            --name emotion-service \
            -p 8000:8000 \
            "$IMAGE_TAG"; then
            
            echo
            print_status "🎉 Success! Updated emotion service is running"
            print_status "🌐 Service URL: http://localhost:8000"
            
            # Show recent logs
            sleep 3
            print_status "Recent startup logs:"
            docker logs --tail 5 emotion-service
            
        else
            print_error "Failed to start container"
            exit 1
        fi
        
    else
        print_error "Failed to build image"
        exit 1
    fi
    
    echo
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    print_header "Build completed successfully! 🎉"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    echo "Your new image: $IMAGE_TAG"
    echo
    echo "Useful commands:"
    echo "  📋 View logs:      docker logs -f emotion-service"
    echo "  ⏹️  Stop service:   docker stop emotion-service"
    echo "  🗑️  Remove:        docker rm emotion-service"
    echo "  🔄 Restart:       docker restart emotion-service"
    echo
}

main "$@"
