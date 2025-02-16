package main

import (
    "log"
    "github.com/yourusername/lang-portal/pkg/database"
    "github.com/yourusername/lang-portal/internal/api/router"
)

func main() {
    // Setup database
    db, err := database.SetupDB()
    if err != nil {
        log.Fatalf("Failed to setup database: %v", err)
    }

    // Setup router
    r := router.SetupRouter(db)

    // Start server
    if err := r.Run(":5000"); err != nil {
        log.Fatalf("Failed to start server: %v", err)
    }
} 