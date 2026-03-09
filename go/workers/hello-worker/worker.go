// hello-worker — minimal Go WCP worker example
//
// Demonstrates the full-package structure for a WCP-compliant Go worker:
// routing rules, registry record, and the AttestationVerifier pattern.
//
// Run: WCP_ATTEST_HMAC_KEY=devsecret go run worker.go
package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/pyhall/pyhall-go/wcp"
)

// WorkerID is the unique deployed-instance identifier for this worker.
// Format: org.<namespace>.<descriptor>[.<instance>]
const WorkerID = "org.example.hello-worker.instance-1"

// WorkerSpeciesID identifies the taxonomy species this worker belongs to.
const WorkerSpeciesID = "wrk.doc.summarizer"

// ---------------------------------------------------------------------------
// Request / response types
// ---------------------------------------------------------------------------

type Request struct {
	Input string `json:"input"`
}

type Response struct {
	Output    string `json:"output"`
	WorkerID  string `json:"worker_id"`
	Timestamp string `json:"timestamp"`
}

// ---------------------------------------------------------------------------
// Handler
// ---------------------------------------------------------------------------

func handleRun(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req Request
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "bad request", http.StatusBadRequest)
		return
	}

	resp := Response{
		Output:    fmt.Sprintf("Hello from %s! You sent: %s", WorkerID, req.Input),
		WorkerID:  WorkerID,
		Timestamp: time.Now().UTC().Format(time.RFC3339),
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resp)
}

// ---------------------------------------------------------------------------
// Attestation check at startup
// ---------------------------------------------------------------------------

func verifyAttestation(packageRoot string) {
	v := &wcp.PackageAttestationVerifier{
		PackageRoot:     packageRoot,
		ManifestPath:    packageRoot + "/manifest.json",
		WorkerID:        WorkerID,
		WorkerSpeciesID: WorkerSpeciesID,
	}

	result := v.Verify()
	if !result.OK {
		log.Printf("WARN: attestation check failed: %s (set WCP_ATTEST_HMAC_KEY for hard attestation)", result.DenyCode)
		// In dev: continue with warning. In prod, set PYHALL_ENV=prod to make this fatal.
		if os.Getenv("PYHALL_ENV") == "prod" {
			log.Fatalf("FATAL: attestation required in prod mode")
		}
		return
	}

	if ts, ok := result.Meta["trust_statement"].(string); ok {
		log.Printf("Attestation OK: %s", ts)
	}
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

func main() {
	// Soft attestation check at startup (hard in prod)
	packageRoot := "."
	if root := os.Getenv("WORKER_PACKAGE_ROOT"); root != "" {
		packageRoot = root
	}
	verifyAttestation(packageRoot)

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	http.HandleFunc("/run", handleRun)
	http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		fmt.Fprintf(w, `{"status":"ok","worker_id":"%s"}`, WorkerID)
	})

	log.Printf("hello-worker listening on :%s", port)
	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatal(err)
	}
}
