package main

import (
	"log"
	"os"

	"github.com/yourusername/lang-portal/internal/api/router"
	"github.com/yourusername/lang-portal/pkg/database"
)

func main() {
	// Setup database
	db, err := database.SetupDB()
	if err != nil {
		log.Fatalf("Failed to setup database: %v", err)
	}

	// Setup router
	r := router.SetupRouter(db)

	// Get port from environment or use default
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	// Start server
	log.Printf("Server starting on port %s...", port)
	if err := r.Run(":" + port); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}
