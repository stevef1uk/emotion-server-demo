#!/bin/bash

# Development helper script for Emotion API Stack
set -e

COMPOSE_FILE="docker-compose.yml"

show_help() {
    echo "Emotion API Development Helper"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start          Start all services"
    echo "  stop           Stop all services"
    echo "  restart        Restart all services"
    echo "  rebuild        Rebuild and start all services"
    echo "  logs           Show logs from all services"
    echo "  logs [service] Show logs from specific service"
    echo "  status         Show service status"
    echo "  shell [service] Open shell in service container"
    echo "  test           Test all endpoints"
    echo "  clean          Stop services and remove volumes"
    echo "  dev-ui         Run only API, develop UI locally"
    echo "  dev-mcp        Run API and UI, develop MCP locally"
    echo "  help           Show this help"
}

start_services() {
    echo "🚀 Starting Emotion API stack..."
    docker-compose up -d
    echo "✅ Services started. Use '$0 status' to check health."
}

stop_services() {
    echo "🛑 Stopping services..."
    docker-compose down
    echo "✅ Services stopped."
}

restart_services() {
    echo "🔄 Restarting services..."
    docker-compose restart
    echo "✅ Services restarted."
}

rebuild_services() {
    echo "🔨 Rebuilding and starting services..."
    docker-compose down
    docker-compose build --no-cache
    docker-compose up -d
    echo "✅ Services rebuilt and started."
}

show_logs() {
    if [ -n "$1" ]; then
        echo "📋 Showing logs for $1..."
        docker-compose logs -f "$1"
    else
        echo "📋 Showing logs for all services..."
        docker-compose logs -f
    fi
}

show_status() {
    echo "📊 Service Status:"
    docker-compose ps
    echo ""
    echo "🔍 Health Checks:"
    
    # Test endpoints with timeout
    test_endpoint() {
        local url=$1
        local name=$2
        if timeout 5 curl -s -f "$url" > /dev/null 2>&1; then
            echo "✅ $name is healthy ($url)"
        else
            echo "❌ $name is not responding ($url)"
        fi
    }
    
    test_endpoint "http://localhost:8000/health" "Emotion API"
    test_endpoint "http://localhost:5001/health" "Python UI"
    test_endpoint "http://localhost:9000/health" "MCP Server"
}

open_shell() {
    if [ -z "$1" ]; then
        echo "❌ Please specify a service: emotion-api, emotion-ui, or emotion-mcp"
        exit 1
    fi
    
    echo "🐚 Opening shell in $1..."
    docker-compose exec "$1" /bin/bash
}

test_endpoints() {
    echo "🧪 Testing all endpoints..."
    echo ""
    
    # Test with proper error handling and user feedback
    test_detailed() {
        local url=$1
        local name=$2
        local method=${3:-GET}
        
        echo -n "Testing $name ($method $url)... "
        
        if [ "$method" = "POST" ]; then
            response=$(curl -s -w "HTTP_CODE:%{http_code}" -X POST \
                -H "Content-Type: application/json" \
                -d '{"text":"I am feeling happy today"}' \
                "$url" 2>/dev/null || echo "HTTP_CODE:000")
        else
            response=$(curl -s -w "HTTP_CODE:%{http_code}" "$url" 2>/dev/null || echo "HTTP_CODE:000")
        fi
        
        http_code=$(echo "$response" | grep -o "HTTP_CODE:[0-9]*" | cut -d: -f2)
        body=$(echo "$response" | sed 's/HTTP_CODE:[0-9]*$//')
        
        if [ "$http_code" = "200" ]; then
            echo "✅ OK"
        elif [ "$http_code" = "000" ]; then
            echo "❌ Connection failed"
        else
            echo "⚠️  HTTP $http_code"
        fi
    }
    
    test_detailed "http://localhost:8000/health" "Emotion API Health"
    test_detailed "http://localhost:5001/health" "UI Health"
    test_detailed "http://localhost:9000/health" "MCP Health"
    test_detailed "http://localhost:5001/predict" "Prediction Endpoint" "POST"
    
    echo ""
    echo "📍 Available endpoints:"
    echo "   • Emotion API: http://localhost:8000"
    echo "   • Python UI: http://localhost:5001"
    echo "   • Prediction API: http://localhost:5001/predict"
    echo "   • MCP Server: http://localhost:9000"
}

clean_services() {
    echo "🧹 Cleaning up services and volumes..."
    docker-compose down -v
    docker system prune -f
    echo "✅ Cleanup complete."
}

dev_ui_mode() {
    echo "🔧 Development mode: API only (for local UI development)"
    echo "Starting emotion-api service..."
    docker-compose up -d emotion-api
    echo ""
    echo "✅ API running on http://localhost:8000"
    echo "🧑‍💻 Now run your UI locally:"
    echo "   cd python_server"
    echo "   export EMOTION_API_URL=http://localhost:8000"
    echo "   python3 emotion_server.py"
}

dev_mcp_mode() {
    echo "🔧 Development mode: API + UI (for local MCP development)"
    echo "Starting emotion-api and emotion-ui services..."
    docker-compose up -d emotion-api emotion-ui
    echo ""
    echo "✅ API running on http://localhost:8000"
    echo "✅ UI running on http://localhost:5001"
    echo "🧑‍💻 Now run your MCP server locally:"
    echo "   cd mcp-go-server"
    echo "   export EMOTION_SERVICE_URL=http://localhost:5001/predict"
    echo "   go run ./main"
}

# Main script logic
case "${1:-help}" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    rebuild)
        rebuild_services
        ;;
    logs)
        show_logs "$2"
        ;;
    status)
        show_status
        ;;
    shell)
        open_shell "$2"
        ;;
    test)
        test_endpoints
        ;;
    clean)
        clean_services
        ;;
    dev-ui)
        dev_ui_mode
        ;;
    dev-mcp)
        dev_mcp_mode
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
