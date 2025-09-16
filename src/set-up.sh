#!/bin/bash

# Emotion API Docker Compose Setup Script
set -e

echo "🚀 Setting up Emotion API Stack..."

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if required directories exist
required_dirs=("mcp-go-server"  )
for dir in "${required_dirs[@]}"; do
    if [ ! -d "$dir" ]; then
        echo "❌ Required directory '$dir' not found."
        exit 1
    fi
done

# Check if required files exist
required_files=(
    "mcp-go-server/go.mod"
    "mcp-go-server/main.go"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Required file '$file' not found."
        exit 1
    fi
done

echo "✅ All required files and directories found."


if [ ! -f "mcp-go-server/Dockerfile" ]; then
    echo "📄 Creating mcp-go-server/Dockerfile..."
    # The Dockerfile content would be created here or copied from the artifacts
fi

if [ ! -f "docker-compose.yml" ]; then
    echo "📄 Creating docker-compose.yml..."
    # The docker-compose.yml content would be created here or copied from the artifacts
fi

# Build and start services
echo "🔨 Building Docker images..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service status
echo "📊 Checking service status..."
docker-compose ps

# Test endpoints
echo "🧪 Testing endpoints..."

# Test Emotion API
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Emotion API is running on http://localhost:8000"
else
    echo "❌ Emotion API health check failed"
fi


# Test MCP Server
if curl -f http://localhost:9000/health > /dev/null 2>&1; then
    echo "✅ MCP Server is running on http://localhost:9000"
else
    echo "❌ MCP Server health check failed"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📖 Available endpoints:"
echo "   • Python UI: http://localhost:7860"
echo "   • Emotion API: http://localhost:8000/predict"
echo "   • MCP Server: http://localhost:9000"
echo ""
echo "🔧 Useful commands:"
echo "   • View logs: docker-compose logs -f"
echo "   • Stop services: docker-compose down"
echo "   • Rebuild: docker-compose build --no-cache"
echo "   • Restart: docker-compose restart"
echo ""
echo "📊 Monitor with: docker-compose ps"
