package main

import (
	"fmt"
	"log"
	"net/http"
)

func main() {
	// Use 0.0.0.0 to bind to all available network interfaces inside the container.
	// This is crucial for Modal to route traffic to the server.
	const port = "8000"
	addr := fmt.Sprintf("0.0.0.0:%s", port)
	
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintf(w, "Hello from a Go web server!")
	})
	
	log.Printf("Server starting on %s...", addr)
	// ListenAndServe blocks until the server stops, which is what we want for a web server.
	log.Fatal(http.ListenAndServe(addr, nil))
}
