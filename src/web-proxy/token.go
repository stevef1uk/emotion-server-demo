package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"sync"
	"time"
)

// TokenManager manages short-lived Bearer tokens minted from the Agent Gateway.
type TokenManager struct {
	tokenURL     string
	delegationID string
	agentSecret  string
	ttlSeconds   int
	client       *http.Client

	mu          sync.RWMutex
	accessToken string
	expiresAt   time.Time
}

// NewTokenManager initializes a manager for gateway Bearer tokens.
func NewTokenManager(tokenURL, delegationID, agentSecret string, ttlSeconds int) *TokenManager {
	if ttlSeconds <= 0 {
		ttlSeconds = 900 // 15 minutes default
	}
	return &TokenManager{
		tokenURL:     tokenURL,
		delegationID: delegationID,
		agentSecret:  agentSecret,
		ttlSeconds:   ttlSeconds,
		client:       &http.Client{Timeout: 15 * time.Second},
	}
}

// GetToken returns a valid cached access token, automatically refreshing when close to expiry.
func (m *TokenManager) GetToken(ctx context.Context) (string, error) {
	m.mu.RLock()
	if m.accessToken != "" && time.Now().Add(60*time.Second).Before(m.expiresAt) {
		tok := m.accessToken
		m.mu.RUnlock()
		return tok, nil
	}
	m.mu.RUnlock()

	m.mu.Lock()
	defer m.mu.Unlock()

	// Double-check after acquiring write lock
	if m.accessToken != "" && time.Now().Add(60*time.Second).Before(m.expiresAt) {
		return m.accessToken, nil
	}

	return m.refreshTokenLocked(ctx)
}

// Invalidate forces eviction of the cached token (e.g. after receiving 401).
func (m *TokenManager) Invalidate() {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.accessToken = ""
	m.expiresAt = time.Time{}
}

func (m *TokenManager) refreshTokenLocked(ctx context.Context) (string, error) {
	if m.delegationID == "" || m.agentSecret == "" {
		return "", fmt.Errorf("DELEGATION_ID and AGENT_SECRET must be configured")
	}

	reqBody, err := json.Marshal(map[string]any{
		"delegation_id": m.delegationID,
		"agent_secret":  m.agentSecret,
		"ttl_seconds":   m.ttlSeconds,
	})
	if err != nil {
		return "", fmt.Errorf("marshal token request: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, m.tokenURL, bytes.NewReader(reqBody))
	if err != nil {
		return "", fmt.Errorf("create token request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := m.client.Do(req)
	if err != nil {
		return "", fmt.Errorf("execute token request to %s: %w", m.tokenURL, err)
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(io.LimitReader(resp.Body, 16384))
	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("token endpoint returned HTTP %d: %s", resp.StatusCode, string(body))
	}

	var res struct {
		AccessToken string `json:"access_token"`
		ExpiresIn   int    `json:"expires_in"`
		TokenType   string `json:"token_type"`
	}
	if err := json.Unmarshal(body, &res); err != nil {
		return "", fmt.Errorf("parse token response: %w", err)
	}
	if res.AccessToken == "" {
		return "", fmt.Errorf("token endpoint returned empty access_token: %s", string(body))
	}

	expiresIn := res.ExpiresIn
	if expiresIn <= 0 {
		expiresIn = m.ttlSeconds
	}

	m.accessToken = res.AccessToken
	m.expiresAt = time.Now().Add(time.Duration(expiresIn) * time.Second)
	return m.accessToken, nil
}
