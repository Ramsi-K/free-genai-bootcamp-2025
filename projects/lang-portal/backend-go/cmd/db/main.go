package main

import (
    "flag"
    "log"
    "github.com/yourusername/lang-portal/pkg/database"
)

func main() {
    initDB := flag.Bool("init", false, "Initialize database")
    seedDB := flag.Bool("seed", false, "Seed database with initial data")
    flag.Parse()

    db, err := database.SetupDB()
    if err != nil {
        log.Fatalf("Failed to setup database: %v", err)
    }

    if *initDB {
        log.Println("Database initialized successfully!")
    }

    if *seedDB {
        if err := database.LoadSeedData(db); err != nil {
            log.Fatalf("Failed to seed database: %v", err)
        }
        log.Println("Database seeded successfully!")
    }
} 