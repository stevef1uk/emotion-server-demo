package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"time"

	mcp "github.com/metoro-io/mcp-golang"
)

type EmotionArgs struct {
	Text string `json:"text"`
}

func handleEmotionDetection(args EmotionArgs) (*mcp.ToolResponse, error) {
	client := &http.Client{Timeout: 30 * time.Second}
	payload, _ := json.Marshal(map[string]string{"text": args.Text})
	url := os.Getenv("EMOTION_SERVICE_URL")
	if url == "" {
		url = "http://localhost:8000/predict"
	}
	resp, err := client.Post(url, "application/json", bytes.NewBuffer(payload))
	if err != nil {
		return nil, fmt.Errorf("request error: %w", err)
	}
	defer resp.Body.Close()
	b, _ := io.ReadAll(resp.Body)
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("emotion api error: %s - %s", resp.Status, string(b))
	}
	var out map[string]any
	if err := json.Unmarshal(b, &out); err != nil {
		return nil, fmt.Errorf("decode error: %w", err)
	}

	// Fixed: Use "emotion" instead of "prediction"
	emotion, _ := out["emotion"].(string)
	conf, _ := out["confidence"].(float64)

	// Simple format without emoji - let UI handle emoji mapping
	msg := fmt.Sprintf("Emotion: %s (Confidence: %.2f%%)", emotion, conf*100)

	log.Printf("emotion_detection: %s", msg)
	return mcp.NewToolResponse(mcp.NewTextContent(msg)), nil
}

// handleEmotionDetectionDetailed calls the detailed prediction endpoint and
// returns the raw JSON response as text content so the UI can render it.
func handleEmotionDetectionDetailed(args EmotionArgs) (*mcp.ToolResponse, error) {
	client := &http.Client{Timeout: 30 * time.Second}
	payload, _ := json.Marshal(map[string]string{"text": args.Text})

	// Prefer a dedicated detailed URL if provided; otherwise derive from EMOTION_SERVICE_URL
	detailedURL := os.Getenv("EMOTION_DETAILED_URL")
	if detailedURL == "" {
		base := os.Getenv("EMOTION_SERVICE_URL")
		if base == "" {
			base = "http://localhost:8000/predict"
		}
		if len(base) >= len("/predict") && base[len(base)-len("/predict"):] == "/predict" {
			detailedURL = base + "_detailed" // results in /predict_detailed
		} else {
			detailedURL = "http://localhost:8000/predict_detailed"
		}
	}

	resp, err := client.Post(detailedURL, "application/json", bytes.NewBuffer(payload))
	if err != nil {
		return nil, fmt.Errorf("request error: %w", err)
	}
	defer resp.Body.Close()
	b, _ := io.ReadAll(resp.Body)
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("emotion api error: %s - %s", resp.Status, string(b))
	}

	// Return the raw JSON as text so the UI can present full details
	return mcp.NewToolResponse(mcp.NewTextContent(string(b))), nil
}
