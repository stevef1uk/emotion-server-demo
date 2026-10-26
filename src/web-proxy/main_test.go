package main

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestHealthEndpoint(t *testing.T) {
	srv := &Server{}
	req := httptest.NewRequest(http.MethodGet, "/healthz", nil)
	rec := httptest.NewRecorder()

	srv.handleHealth(rec, req)
	if rec.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d", rec.Code)
	}
	if !strings.Contains(rec.Body.String(), `"status":"ok"`) {
		t.Fatalf("unexpected body: %s", rec.Body.String())
	}
}

func TestIndexEndpoint(t *testing.T) {
	srv := &Server{}
	req := httptest.NewRequest(http.MethodGet, "/", nil)
	rec := httptest.NewRecorder()

	srv.handleIndex(rec, req)
	if rec.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d", rec.Code)
	}
	if !strings.Contains(rec.Body.String(), "Emotion Detection Service") {
		t.Fatalf("expected HTML title, got %s", rec.Body.String())
	}
}

func TestEmptyTextValidation(t *testing.T) {
	srv := &Server{}
	req := httptest.NewRequest(http.MethodPost, "/api/analyze", strings.NewReader(`{"text":""}`))
	rec := httptest.NewRecorder()

	srv.handleAnalyze(rec, req)
	if rec.Code != http.StatusBadRequest {
		t.Fatalf("expected 400 for empty text, got %d", rec.Code)
	}
	var res AnalyzeResponse
	if err := json.Unmarshal(rec.Body.Bytes(), &res); err != nil {
		t.Fatal(err)
	}
	if res.Status != "error" {
		t.Fatalf("expected error status, got %s", res.Status)
	}
}
