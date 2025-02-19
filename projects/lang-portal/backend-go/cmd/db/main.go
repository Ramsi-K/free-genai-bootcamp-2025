package main

import (
	"flag"
	"log"
	"os"

	"github.com/Ramsi-K/free-genai-bootcamp-2025/projects/lang-portal/backend-go/pkg/database"
)

func main() {
	// Parse command line flags
	init := flag.Bool("init", false, "Initialize the database")
	seed := flag.Bool("seed", false, "Seed the database with initial data")
	verify := flag.Bool("verify", false, "Verify database schema and data")
	flag.Parse()

	// If no flags are provided, show usage
	if !*init && !*seed && !*verify {
		log.Println("No action specified. Use -init to initialize database, -seed to seed data, or -verify to verify schema.")
		flag.Usage()
		os.Exit(1)
	}

	// Initialize database if requested
	if *init {
		log.Println("Initializing database...")
		db, err := database.InitDB("test.db")
		if err != nil {
			log.Fatalf("Failed to initialize database: %v", err)
		}
		sqlDB, err := db.DB()
		if err != nil {
			log.Fatalf("Failed to get database instance: %v", err)
		}
		if err := sqlDB.Close(); err != nil {
			log.Printf("Warning: failed to close database connection: %v", err)
		}
		log.Println("Database initialized successfully")
	}

	// Get database instance for other operations
	db, err := database.SetupDB()
	if err != nil {
		log.Fatalf("Failed to setup database: %v", err)
	}

	// Verify database schema if requested
	if *verify {
		log.Println("Verifying database schema...")
		if err := database.VerifyDB(db); err != nil {
			log.Fatalf("Database verification failed: %v", err)
		}
		log.Println("Database schema verified successfully")
	}

	// Seed database if requested
	if *seed {
		// Verify schema before seeding
		if err := database.VerifyDB(db); err != nil {
			log.Fatalf("Cannot seed database, schema verification failed: %v", err)
		}

		log.Println("Seeding database...")
		if err := database.LoadSeedData(db); err != nil {
			log.Fatalf("Failed to seed database: %v", err)
		}
		log.Println("Database seeded successfully")
	}
}
