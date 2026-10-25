package main

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"strings"
	"testing"

	"github.com/mark3labs/mcp-go/mcp"
	"github.com/mark3labs/mcp-go/server"
)

func TestHealthHandler(t *testing.T) {
	req := httptest.NewRequest(http.MethodGet, "/health", nil)
	rr := httptest.NewRecorder()

	healthHandler(rr, req)

	if rr.Code != http.StatusOK {
		t.Fatalf("expected status 200, got %d", rr.Code)
	}

	var resp map[string]any
	if err := json.Unmarshal(rr.Body.Bytes(), &resp); err != nil {
		t.Fatalf("failed to decode response: %v", err)
	}

	if resp["status"] != "healthy" {
		t.Errorf("expected status 'healthy', got %v", resp["status"])
	}
	if resp["service"] != serverName {
		t.Errorf("expected service '%s', got %v", serverName, resp["service"])
	}
}

func TestHandleEmotionDetectionMissingText(t *testing.T) {
	req := mcp.CallToolRequest{
		Params: mcp.CallToolParams{
			Name:      "emotion_detection",
			Arguments: map[string]interface{}{},
		},
	}

	res, err := handleEmotionDetection(context.Background(), req)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !res.IsError {
		t.Errorf("expected error result when text is missing")
	}
}

func TestHandleEmotionDetectionSuccess(t *testing.T) {
	mockBackend := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			t.Errorf("expected POST, got %s", r.Method)
		}
		var req map[string]string
		_ = json.NewDecoder(r.Body).Decode(&req)
		if req["text"] != "I am so happy!" {
			t.Errorf("expected 'I am so happy!', got '%s'", req["text"])
		}

		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(map[string]any{
			"emotion":    "happiness",
			"confidence": 0.985,
		})
	}))
	defer mockBackend.Close()

	os.Setenv("EMOTION_SERVICE_URL", mockBackend.URL+"/predict")
	defer os.Unsetenv("EMOTION_SERVICE_URL")

	req := mcp.CallToolRequest{
		Params: mcp.CallToolParams{
			Name: "emotion_detection",
			Arguments: map[string]interface{}{
				"text":     "I am so happy!",
				"accurate": true,
			},
		},
	}

	res, err := handleEmotionDetection(context.Background(), req)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if res.IsError {
		t.Fatalf("expected success, got error result")
	}

	textContent := res.Content[0].(mcp.TextContent).Text
	expected := "Emotion: happiness (Confidence: 98.50%)"
	if textContent != expected {
		t.Errorf("expected %q, got %q", expected, textContent)
	}
}

func TestHandleEmotionDetectionDetailedSuccess(t *testing.T) {
	mockBackend := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(map[string]any{
			"predicted_emotion": "happiness",
			"confidence":        0.985,
			"all_emotions": map[string]float64{
				"happiness": 0.985,
				"sadness":   0.005,
				"neutral":   0.010,
			},
		})
	}))
	defer mockBackend.Close()

	os.Setenv("EMOTION_DETAILED_URL", mockBackend.URL+"/predict_detailed")
	defer os.Unsetenv("EMOTION_DETAILED_URL")

	req := mcp.CallToolRequest{
		Params: mcp.CallToolParams{
			Name: "emotion_detection_detailed",
			Arguments: map[string]interface{}{
				"text": "I am so happy!",
			},
		},
	}

	res, err := handleEmotionDetectionDetailed(context.Background(), req)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if res.IsError {
		t.Fatalf("expected success, got error result")
	}

	textContent := res.Content[0].(mcp.TextContent).Text
	var parsed map[string]any
	if err := json.Unmarshal([]byte(textContent), &parsed); err != nil {
		t.Fatalf("expected valid JSON in detailed text content, got: %v", err)
	}
	if parsed["predicted_emotion"] != "happiness" {
		t.Errorf("expected predicted_emotion happiness, got %v", parsed["predicted_emotion"])
	}
}


func TestStreamableHTTPEndpoint(t *testing.T) {
	mcpServer := server.NewMCPServer(
		serverName,
		serverVersion,
		server.WithToolCapabilities(true),
	)
	registerTools(mcpServer)

	httpServer := server.NewStreamableHTTPServer(
		mcpServer,
		server.WithStateLess(true),
		server.WithEndpointPath("/mcp"),
	)

	// Test tools/list
	reqBody := `{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}`
	req := httptest.NewRequest(http.MethodPost, "/mcp", strings.NewReader(reqBody))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Accept", "application/json, text/event-stream")

	rr := httptest.NewRecorder()
	httpServer.ServeHTTP(rr, req)

	if rr.Code != http.StatusOK {
		t.Fatalf("expected status 200, got %d (body: %s)", rr.Code, rr.Body.String())
	}

	var jsonResp map[string]any
	if err := json.Unmarshal(rr.Body.Bytes(), &jsonResp); err != nil {
		t.Fatalf("failed to parse JSON-RPC response: %v", err)
	}

	result, ok := jsonResp["result"].(map[string]any)
	if !ok {
		t.Fatalf("expected 'result' in response: %v", jsonResp)
	}

	tools, ok := result["tools"].([]any)
	if !ok || len(tools) != 2 {
		t.Fatalf("expected 2 tools, got %v", tools)
	}
}
