package handlers

import (
	"fmt"
	"log"
	"testing"

	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/models"
	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/pkg/database"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

// TestData struct to hold all test data
type TestData struct {
	TestWord1    *models.Word
	TestWord2    *models.Word
	TestGroup    *models.WordGroup
	TestActivity *models.StudyActivity
}

// setupTestDB initializes a test database
func setupTestDB(t *testing.T) (*gorm.DB, error) {
	db, err := gorm.Open(sqlite.Open(":memory:"), &gorm.Config{})
	if err != nil {
		return nil, fmt.Errorf("failed to create test database: %w", err)
	}

	// Auto-migrate schema
	if err := db.AutoMigrate(
		&models.Word{},
		&models.Translation{},
		&models.Sentence{},
		&models.WordGroup{},
		&models.GROUP_Word{},
		&models.GROUP_Translation{},
		&models.StudyActivity{},
		&models.StudySession{},
		&models.WordReviewItem{},
	); err != nil {
		return nil, fmt.Errorf("failed to migrate test database: %w", err)
	}

	// Seed test data using the new function
	if err := database.SeedTestDB(db); err != nil {
		return nil, fmt.Errorf("failed to seed test database: %w", err)
	}

	return db, nil
}

// cleanupTestDB closes the database connection
func cleanupTestDB(db *gorm.DB) error {
	sqlDB, err := db.DB()
	if err != nil {
		return fmt.Errorf("failed to get database: %w", err)
	}

	if err := sqlDB.Close(); err != nil {
		return fmt.Errorf("failed to close database: %w", err)
	}

	return nil
}

// resetTestDB resets the database for fresh testing
func resetTestDB(db *gorm.DB) error {
	log.Println("⚡ Resetting test database...")

	// Drop all tables
	err := db.Migrator().DropTable(
		&models.StudySession{},
		&models.WordReviewItem{},
		"group_words",
		&models.GROUP_Word{},
		&models.GROUP_Translation{},
		&models.Word{},
		&models.WordGroup{},
		&models.StudyActivity{},
	)
	if err != nil {
		log.Printf("⚠️ Error dropping tables: %v", err)
		return err
	}

	// Run migrations
	err = db.AutoMigrate(
		&models.Word{},
		&models.Translation{},
		&models.Sentence{},
		&models.WordGroup{},
		&models.GROUP_Word{},
		&models.GROUP_Translation{},
		&models.StudyActivity{},
		&models.StudySession{},
		&models.WordReviewItem{},
	)
	if err != nil {
		log.Printf("⚠️ Error running migrations: %v", err)
		return err
	}

	// Use SeedTestDB instead of setupTestData
	if err := database.SeedTestDB(db); err != nil {
		log.Printf("⚠️ Error seeding test data: %v", err)
		return err
	}

	log.Println("✅ Test database reset successfully!")
	return nil
}

// withCleanDB runs a test function with a clean database
func withCleanDB(t *testing.T, db *gorm.DB, testFunc func()) {
	// Start a transaction
	tx := db.Begin()
	if tx.Error != nil {
		t.Fatalf("Failed to begin transaction: %v", tx.Error)
	}

	// Defer rollback in case of panic
	defer func() {
		if r := recover(); r != nil {
			tx.Rollback()
			t.Fatalf("Test panicked: %v", r)
		}
	}()

	// Run the test function with the transactional DB
	testFunc()

	// Rollback the transaction
	if err := tx.Rollback().Error; err != nil {
		t.Fatalf("Failed to rollback: %v", err)
	}
}
