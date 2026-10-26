package main

import (
	"bytes"
	_ "embed"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"regexp"
	"strconv"
	"strings"
	"time"
)

//go:embed static/index.html
var indexHTML []byte

type Config struct {
	Port            string
	GatewayTokenURL string
	GatewayMCPURL   string
	DelegationID    string
	AgentSecret     string
	TokenTTL        int
}

func loadConfig() Config {
	port := os.Getenv("PORT")
	if port == "" {
		port = ":8080"
	}
	if !strings.HasPrefix(port, ":") {
		port = ":" + port
	}

	tokenURL := os.Getenv("GATEWAY_TOKEN_URL")
	if tokenURL == "" {
		tokenURL = "https://preprod.agw.sjfisher.com/token"
	}

	mcpURL := os.Getenv("GATEWAY_MCP_URL")
	if mcpURL == "" {
		mcpURL = "https://preprod.agw.sjfisher.com/mcp-emotion"
	}

	ttl, _ := strconv.Atoi(os.Getenv("TOKEN_TTL"))
	if ttl <= 0 {
		ttl = 900 // 15 minutes
	}

	return Config{
		Port:            port,
		GatewayTokenURL: tokenURL,
		GatewayMCPURL:   mcpURL,
		DelegationID:    os.Getenv("DELEGATION_ID"),
		AgentSecret:     os.Getenv("AGENT_SECRET"),
		TokenTTL:        ttl,
	}
}

type Server struct {
	cfg          Config
	tokenManager *TokenManager
	httpClient   *http.Client
}

func main() {
	cfg := loadConfig()
	log.Printf("Starting Emotion Web Proxy on %s (MCP: %s)", cfg.Port, cfg.GatewayMCPURL)
	if cfg.DelegationID == "" || cfg.AgentSecret == "" {
		log.Printf("WARNING: DELEGATION_ID or AGENT_SECRET not set. Calls to gateway will fail until configured.")
	}

	tm := NewTokenManager(cfg.GatewayTokenURL, cfg.DelegationID, cfg.AgentSecret, cfg.TokenTTL)
	srv := &Server{
		cfg:          cfg,
		tokenManager: tm,
		httpClient:   &http.Client{Timeout: 30 * time.Second},
	}

	mux := http.NewServeMux()
	mux.HandleFunc("GET /healthz", srv.handleHealth)
	mux.HandleFunc("GET /api/emotion/healthz", srv.handleHealth)
	mux.HandleFunc("GET /{$}", srv.handleIndex)
	mux.HandleFunc("/api/analyze", srv.handleAnalyze)
	mux.HandleFunc("/api/emotion/analyze", srv.handleAnalyze)

	httpServer := &http.Server{
		Addr:         cfg.Port,
		Handler:      mux,
		ReadTimeout:  15 * time.Second,
		WriteTimeout: 45 * time.Second,
	}

	log.Fatal(httpServer.ListenAndServe())
}

func (s *Server) handleHealth(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	_, _ = w.Write([]byte(`{"status":"ok"}`))
}

func (s *Server) handleIndex(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	w.Header().Set("Cache-Control", "no-cache, no-store, must-revalidate")
	_, _ = w.Write(indexHTML)
}

type AnalyzeRequest struct {
	Text     string `json:"text"`
	Detailed bool   `json:"detailed"`
}

type AnalyzeResponse struct {
	Status         string             `json:"status"`
	Tool           string             `json:"tool,omitempty"`
	PrimaryEmotion string             `json:"primary_emotion,omitempty"`
	Confidence     float64            `json:"confidence,omitempty"`
	AllEmotions    map[string]float64 `json:"all_emotions,omitempty"`
	ApprovalID     string             `json:"approval_id,omitempty"`
	Reason         string             `json:"reason,omitempty"`
	Error          string             `json:"error,omitempty"`
	Raw            string             `json:"raw,omitempty"`
}

var textOutputRegex = regexp.MustCompile(`(?i)emotion:\s*([a-z]+)\s*\(\s*confidence:\s*([0-9.]+)%\s*\)`)

func (s *Server) handleAnalyze(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	var req AnalyzeRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		w.WriteHeader(http.StatusBadRequest)
		_ = json.NewEncoder(w).Encode(AnalyzeResponse{Status: "error", Error: "invalid JSON body"})
		return
	}

	req.Text = strings.TrimSpace(req.Text)
	if req.Text == "" {
		w.WriteHeader(http.StatusBadRequest)
		_ = json.NewEncoder(w).Encode(AnalyzeResponse{Status: "error", Error: "text cannot be empty"})
		return
	}
	if len(req.Text) > 2000 {
		req.Text = req.Text[:2000]
	}

	toolName := "emotion_detection"
	if req.Detailed {
		toolName = "emotion_detection_detailed"
	}

	token, err := s.tokenManager.GetToken(r.Context())
	if err != nil {
		log.Printf("token error: %v", err)
		w.WriteHeader(http.StatusInternalServerError)
		_ = json.NewEncoder(w).Encode(AnalyzeResponse{
			Status: "error",
			Error:  "Failed to obtain gateway authorization credential: " + err.Error(),
		})
		return
	}

	// Prepare JSON-RPC 2.0 payload
	rpcPayload := map[string]any{
		"jsonrpc": "2.0",
		"id":      time.Now().UnixNano(),
		"method":  "tools/call",
		"params": map[string]any{
			"name": toolName,
			"arguments": map[string]any{
				"text": req.Text,
			},
		},
	}
	payloadBytes, _ := json.Marshal(rpcPayload)

	httpReq, err := http.NewRequestWithContext(r.Context(), http.MethodPost, s.cfg.GatewayMCPURL, bytes.NewReader(payloadBytes))
	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		_ = json.NewEncoder(w).Encode(AnalyzeResponse{Status: "error", Error: err.Error()})
		return
	}
	httpReq.Header.Set("Authorization", "Bearer "+token)
	httpReq.Header.Set("Content-Type", "application/json")

	resp, err := s.httpClient.Do(httpReq)
	if err != nil {
		log.Printf("gateway call error: %v", err)
		w.WriteHeader(http.StatusBadGateway)
		_ = json.NewEncoder(w).Encode(AnalyzeResponse{Status: "error", Error: "Gateway unreachable: " + err.Error()})
		return
	}
	defer resp.Body.Close()

	respBody, _ := io.ReadAll(io.LimitReader(resp.Body, 65536))

	// Handle 202 Accepted (Human-in-the-Loop Hold)
	if resp.StatusCode == http.StatusAccepted {
		var heldData struct {
			Status     string `json:"status"`
			ApprovalID string `json:"approval_id"`
			Reason     string `json:"reason"`
			Message    string `json:"message"`
		}
		_ = json.Unmarshal(respBody, &heldData)

		_ = json.NewEncoder(w).Encode(AnalyzeResponse{
			Status:     "approval_required",
			Tool:       toolName,
			ApprovalID: heldData.ApprovalID,
			Reason:     heldData.Reason,
			Raw:        string(respBody),
		})
		return
	}

	// Handle 401 Unauthorized (token revoked or expired early)
	if resp.StatusCode == http.StatusUnauthorized {
		s.tokenManager.Invalidate()
		w.WriteHeader(http.StatusUnauthorized)
		_ = json.NewEncoder(w).Encode(AnalyzeResponse{
			Status: "error",
			Error:  "Gateway authentication refused token (invalidated for next request).",
		})
		return
	}

	if resp.StatusCode != http.StatusOK {
		w.WriteHeader(resp.StatusCode)
		_ = json.NewEncoder(w).Encode(AnalyzeResponse{
			Status: "error",
			Error:  fmt.Sprintf("Gateway returned HTTP %d: %s", resp.StatusCode, string(respBody)),
		})
		return
	}

	// Parse JSON-RPC tool result
	var rpcResp struct {
		Result struct {
			Content []struct {
				Type string `json:"type"`
				Text string `json:"text"`
			} `json:"content"`
			IsError bool `json:"isError"`
		} `json:"result"`
		Error *struct {
			Code    int    `json:"code"`
			Message string `json:"message"`
		} `json:"error"`
	}

	if err := json.Unmarshal(respBody, &rpcResp); err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		_ = json.NewEncoder(w).Encode(AnalyzeResponse{Status: "error", Error: "Invalid JSON-RPC from MCP server: " + err.Error()})
		return
	}

	if rpcResp.Error != nil {
		w.WriteHeader(http.StatusBadRequest)
		_ = json.NewEncoder(w).Encode(AnalyzeResponse{Status: "error", Error: rpcResp.Error.Message})
		return
	}

	rawText := ""
	for _, c := range rpcResp.Result.Content {
		if c.Type == "text" {
			rawText += c.Text
		}
	}

	res := AnalyzeResponse{
		Status: "success",
		Tool:   toolName,
		Raw:    rawText,
	}

	// Try unmarshaling detailed JSON structure first
	var detailed struct {
		PredictedEmotion string             `json:"predicted_emotion"`
		Confidence       float64            `json:"confidence"`
		AllEmotions      map[string]float64 `json:"all_emotions"`
	}
	if err := json.Unmarshal([]byte(rawText), &detailed); err == nil && detailed.PredictedEmotion != "" {
		res.PrimaryEmotion = detailed.PredictedEmotion
		res.Confidence = detailed.Confidence
		res.AllEmotions = detailed.AllEmotions
	} else if matches := textOutputRegex.FindStringSubmatch(rawText); len(matches) == 3 {
		// Fallback for standard text format: Emotion: happiness (Confidence: 98.50%)
		res.PrimaryEmotion = matches[1]
		confVal, _ := strconv.ParseFloat(matches[2], 64)
		res.Confidence = confVal / 100.0
	} else {
		res.PrimaryEmotion = "detected"
		res.Confidence = 1.0
	}

	_ = json.NewEncoder(w).Encode(res)
}
