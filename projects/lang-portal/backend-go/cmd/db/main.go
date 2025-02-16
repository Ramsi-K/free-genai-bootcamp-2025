package main

import (
	"flag"
	"log"

	"github.com/Ramsi-K/free-genai-bootcamp-2025/tree/main/projects/lang-portal/backend-go/pkg/database"
)

func main() {
	initDB := flag.Bool("init", false, "Initialize database")
	seedDB := flag.Bool("seed", false, "Seed database with initial data")
	verifyDB := flag.Bool("verify", false, "Verify database contents")
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

	if *verifyDB {
		if err := database.VerifyData(db); err != nil {
			log.Fatalf("Database verification failed: %v", err)
		}
	}
}
