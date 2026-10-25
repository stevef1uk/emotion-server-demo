package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/mark3labs/mcp-go/mcp"
)

var httpClient = &http.Client{
	Timeout: 30 * time.Second,
}

// getEmotionServiceURL returns the base /predict URL from environment or default.
func getEmotionServiceURL() string {
	url := os.Getenv("EMOTION_SERVICE_URL")
	if url == "" {
		url = "http://localhost:8000/predict"
	}
	return url
}

// getEmotionDetailedURL returns the /predict_detailed URL.
func getEmotionDetailedURL() string {
	detailedURL := os.Getenv("EMOTION_DETAILED_URL")
	if detailedURL != "" {
		return detailedURL
	}
	base := getEmotionServiceURL()
	if strings.HasSuffix(base, "/predict") {
		return strings.TrimSuffix(base, "/predict") + "/predict_detailed"
	}
	return "http://localhost:8000/predict_detailed"
}

const commercialLicenseNotice = "Emotion Service API License Required: The emotion detection model is encrypted and protected. Running locally via Docker Compose requires a valid customer private key and license. When running from the public repository without a mounted license key, the model remains locked. To obtain access or a commercial license, please visit https://emotion-service-api.sjfisher.com or contact sales@sjfisher.com."

// handleEmotionDetection calls the /predict endpoint and formats the primary emotion result.
func handleEmotionDetection(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	args := request.GetArguments()
	text, _ := args["text"].(string)
	if strings.TrimSpace(text) == "" {
		return mcp.NewToolResultError("parameter 'text' is required and must not be empty"), nil
	}

	// accurate defaults to true unless explicitly false
	accurate := true
	if accVal, ok := args["accurate"].(bool); ok {
		accurate = accVal
	}

	payload, err := json.Marshal(map[string]string{"text": text})
	if err != nil {
		return mcp.NewToolResultError(fmt.Sprintf("failed to encode request: %v", err)), nil
	}

	url := getEmotionServiceURL()
	if accurate {
		if strings.Contains(url, "?") {
			url += "&accurate=1"
		} else {
			url += "?accurate=1"
		}
	}

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, url, bytes.NewBuffer(payload))
	if err != nil {
		return mcp.NewToolResultError(fmt.Sprintf("failed to create request: %v", err)), nil
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := httpClient.Do(req)
	if err != nil {
		return mcp.NewToolResultError(fmt.Sprintf("%s\n\n(Backend notice: unable to reach emotion-api at %s: %v)", commercialLicenseNotice, url, err)), nil
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return mcp.NewToolResultError(fmt.Sprintf("failed to read response: %v", err)), nil
	}

	if resp.StatusCode != http.StatusOK {
		return mcp.NewToolResultError(fmt.Sprintf("%s\n\n(Backend returned HTTP %d: %s)", commercialLicenseNotice, resp.StatusCode, string(body))), nil
	}

	var out map[string]any
	if err := json.Unmarshal(body, &out); err != nil {
		return mcp.NewToolResultError(fmt.Sprintf("failed to parse emotion API response: %v", err)), nil
	}

	// Handle both "emotion" and "predicted_emotion" fields
	emotion, _ := out["emotion"].(string)
	if emotion == "" {
		emotion, _ = out["predicted_emotion"].(string)
	}

	var conf float64
	if c, ok := out["confidence"].(float64); ok {
		conf = c
	}

	resultMsg := fmt.Sprintf("Emotion: %s (Confidence: %.2f%%)", emotion, conf*100)
	log.Printf("[tools] emotion_detection: %s", resultMsg)
	return mcp.NewToolResultText(resultMsg), nil
}

// handleEmotionDetectionDetailed calls the /predict_detailed endpoint and returns raw JSON.
func handleEmotionDetectionDetailed(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	args := request.GetArguments()
	text, _ := args["text"].(string)
	if strings.TrimSpace(text) == "" {
		return mcp.NewToolResultError("parameter 'text' is required and must not be empty"), nil
	}

	payload, err := json.Marshal(map[string]string{"text": text})
	if err != nil {
		return mcp.NewToolResultError(fmt.Sprintf("failed to encode request: %v", err)), nil
	}

	url := getEmotionDetailedURL()
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, url, bytes.NewBuffer(payload))
	if err != nil {
		return mcp.NewToolResultError(fmt.Sprintf("failed to create request: %v", err)), nil
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := httpClient.Do(req)
	if err != nil {
		return mcp.NewToolResultError(fmt.Sprintf("%s\n\n(Backend notice: unable to reach emotion-api at %s: %v)", commercialLicenseNotice, url, err)), nil
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return mcp.NewToolResultError(fmt.Sprintf("failed to read response: %v", err)), nil
	}

	if resp.StatusCode != http.StatusOK {
		return mcp.NewToolResultError(fmt.Sprintf("%s\n\n(Backend returned HTTP %d: %s)", commercialLicenseNotice, resp.StatusCode, string(body))), nil
	}

	log.Printf("[tools] emotion_detection_detailed: processed %d bytes response", len(body))
	return mcp.NewToolResultText(string(body)), nil
}
