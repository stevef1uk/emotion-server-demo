package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
)

// main function to set up and run the web server.
func main() {
	// The Go server will run on port 8000 inside the container.
	port := getEnv("PORT", "8000")

	// Set up handlers for our web endpoints.
	http.HandleFunc("/health", healthHandler)
	http.HandleFunc("/", homeHandler)

	// Start the server and listen for incoming requests.
	log.Printf("Starting simple Go web server on port %s...", port)
	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatalf("server failed: %v", err)
	}
}

// healthHandler responds to a GET request at /health with an OK status.
func healthHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != "GET" {
		http.Error(w, "Method Not Allowed", http.StatusMethodNotAllowed)
		return
	}
	fmt.Fprintf(w, "OK")
}

// homeHandler responds to a GET request at / with a welcome message.
func homeHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != "GET" {
		http.Error(w, "Method Not Allowed", http.StatusMethodNotAllowed)
		return
	}
	fmt.Fprintf(w, "Hello from a Modal-deployed Go server!")
}

// getEnv retrieves an environment variable or returns a default value.
func getEnv(key, def string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return def
}
