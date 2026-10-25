package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"runtime"
	"strconv"
	"syscall"
	"time"

	"github.com/mark3labs/mcp-go/mcp"
	"github.com/mark3labs/mcp-go/server"
)

const (
	serverName    = "Emotion Detection MCP Server"
	serverVersion = "1.0.0"
)

func main() {
	host := os.Getenv("MCP_HOST")
	if host == "" {
		host = os.Getenv("HOST")
	}
	if host == "" {
		host = "0.0.0.0"
	}

	portStr := os.Getenv("MCP_PORT")
	if portStr == "" {
		portStr = os.Getenv("MCP_SERVER_PORT")
	}
	if portStr == "" {
		portStr = os.Getenv("PORT")
	}
	if portStr == "" {
		portStr = "9000"
	}

	port, err := strconv.Atoi(portStr)
	if err != nil {
		log.Fatalf("Invalid port number: %s", portStr)
	}

	transport := os.Getenv("MCP_TRANSPORT")
	if transport == "" {
		transport = "dual" // supports both streamable-http and sse simultaneously
	}

	mcpServer := server.NewMCPServer(
		serverName,
		serverVersion,
		server.WithToolCapabilities(true),
		server.WithResourceCapabilities(true, false),
		server.WithPromptCapabilities(true),
	)

	registerTools(mcpServer)
	registerResources(mcpServer)
	registerPrompts(mcpServer)

	if transport == "stdio" {
		log.Printf("Starting %s v%s on stdio transport", serverName, serverVersion)
		if err := server.ServeStdio(mcpServer); err != nil {
			log.Fatalf("Stdio server error: %v", err)
		}
		return
	}

	// HTTP-based transport (dual: streamable-http + SSE)
	addr := fmt.Sprintf("%s:%d", host, port)
	mux := http.NewServeMux()

	// Health and readiness endpoints
	mux.HandleFunc("/health", healthHandler)
	mux.HandleFunc("/healthz", healthHandler)
	mux.HandleFunc("/ready", healthHandler)

	// Streamable HTTP endpoint (/mcp) for modern MCP clients (Agent Gateway, Claude, Inspector)
	httpServer := server.NewStreamableHTTPServer(
		mcpServer,
		server.WithStateLess(true),
		server.WithEndpointPath("/mcp"),
	)
	mux.Handle("/mcp", httpServer)
	mux.Handle("/mcp/", httpServer)

	// SSE transport (/sse, /message) for Gradio UI and SSE clients
	sseServer := server.NewSSEServer(mcpServer)
	mux.Handle("/sse", sseServer.SSEHandler())
	mux.Handle("/message", sseServer.MessageHandler())
	mux.Handle("/message/", sseServer.MessageHandler())

	srv := &http.Server{
		Addr:         addr,
		Handler:      mux,
		ReadTimeout:  60 * time.Second,
		WriteTimeout: 60 * time.Second,
	}

	log.Printf("Starting %s v%s on %s [dual: Streamable-HTTP @ /mcp, SSE @ /sse]", serverName, serverVersion, addr)
	log.Printf("Backend Emotion Service URL: %s", getEmotionServiceURL())

	// Graceful shutdown handling
	idleConnsClosed := make(chan struct{})
	go func() {
		sigint := make(chan os.Signal, 1)
		signal.Notify(sigint, os.Interrupt, syscall.SIGTERM)
		<-sigint

		log.Println("Shutting down server gracefully...")
		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()
		if err := srv.Shutdown(ctx); err != nil {
			log.Printf("HTTP server shutdown error: %v", err)
		}
		close(idleConnsClosed)
	}()

	if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		log.Fatalf("Server failed: %v", err)
	}

	<-idleConnsClosed
	log.Println("Server stopped")
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	resp := map[string]any{
		"status":      "healthy",
		"service":     serverName,
		"version":     serverVersion,
		"arch":        fmt.Sprintf("%s/%s", runtime.GOOS, runtime.GOARCH),
		"backend_url": getEmotionServiceURL(),
	}
	_ = json.NewEncoder(w).Encode(resp)
}

func registerTools(s *server.MCPServer) {
	// Tool 1: emotion_detection
	detectionTool := mcp.NewTool("emotion_detection",
		mcp.WithDescription("Analyze text to detect primary emotion using the fine-tuned Gemma model"),
		mcp.WithString("text", mcp.Required(), mcp.Description("The text to analyze for emotion")),
		mcp.WithBoolean("accurate", mcp.Description("Whether to use accurate inference mode (default: true)")),
	)
	s.AddTool(detectionTool, handleEmotionDetection)

	// Tool 2: emotion_detection_detailed
	detailedTool := mcp.NewTool("emotion_detection_detailed",
		mcp.WithDescription("Detailed emotion analysis returning probabilities across all 14 emotion categories"),
		mcp.WithString("text", mcp.Required(), mcp.Description("The text to analyze for detailed emotion probabilities")),
		mcp.WithBoolean("accurate", mcp.Description("Whether to use accurate inference mode (default: false)")),
	)
	s.AddTool(detailedTool, handleEmotionDetectionDetailed)
}

func registerResources(s *server.MCPServer) {
	configResource := mcp.NewResource(
		"config://server",
		"Server Configuration",
		mcp.WithResourceDescription("Current MCP Emotion Server configuration, backend URL, and architecture"),
		mcp.WithMIMEType("application/json"),
	)
	s.AddResource(configResource, configResourceHandler)
}

func configResourceHandler(ctx context.Context, request mcp.ReadResourceRequest) ([]mcp.ResourceContents, error) {
	content := map[string]any{
		"server":      serverName,
		"version":     serverVersion,
		"os":          runtime.GOOS,
		"arch":        runtime.GOARCH,
		"backend_url": getEmotionServiceURL(),
		"tools":       []string{"emotion_detection", "emotion_detection_detailed"},
	}
	b, _ := json.MarshalIndent(content, "", "  ")

	return []mcp.ResourceContents{
		mcp.TextResourceContents{
			URI:      request.Params.URI,
			MIMEType: "application/json",
			Text:     string(b),
		},
	}, nil
}

func registerPrompts(s *server.MCPServer) {
	prompt := mcp.NewPrompt("analyze_emotion",
		mcp.WithPromptDescription("Analyze the emotional tone of a given text and suggest an empathetic response"),
		mcp.WithArgument("text", mcp.ArgumentDescription("The customer or user message to analyze"), mcp.RequiredArgument()),
	)
	s.AddPrompt(prompt, func(ctx context.Context, request mcp.GetPromptRequest) (*mcp.GetPromptResult, error) {
		text := request.Params.Arguments["text"]
		promptContent := fmt.Sprintf(
			"Please use the emotion_detection tool to analyze the emotional state in the following message:\n\n\"%s\"\n\n"+
				"Based on the detected emotion, provide an empathetic, constructive response suitable for customer interaction.",
			text,
		)
		return &mcp.GetPromptResult{
			Description: fmt.Sprintf("Emotion analysis prompt for: %s", text),
			Messages: []mcp.PromptMessage{
				{
					Role: mcp.RoleUser,
					Content: mcp.TextContent{
						Type: "text",
						Text: promptContent,
					},
				},
			},
		}, nil
	})
}
