package main

import (
	"log"

	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/api/router"
	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/pkg/database"
)

func main() {
	// Initialize database
	if err := database.Initialize(); err != nil {
		log.Fatalf("Failed to initialize database: %v", err)
	}

	// Create and setup router
	r := router.SetupRouter()

	// Start server
	if err := r.Run(":8080"); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}
