package main

import (
	"log"

	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/api/router"
	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/models"
	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/pkg/database"
)

func main() {
	// Initialize database
	err := database.Initialize()
	if err != nil {
		log.Fatalf("Failed to initialize database: %v", err)
	}

	db := database.GetDB()
	// AutoMigrate will create/update tables based on your models
	err = db.AutoMigrate(&models.WordGroup{}, &models.GROUP_Word{}, &models.GROUP_Translation{})
	if err != nil {
		log.Fatalf("Failed to auto-migrate database: %v", err)
	}

	// Create and setup router
	r := router.SetupRouter(db)

	// Start server
	if err := r.Run(":8080"); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}
