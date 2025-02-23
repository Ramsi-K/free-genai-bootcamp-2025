package handlers

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
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

func SeedTestDB(db *gorm.DB) error {
	// Drop and recreate tables first
	if err := resetTestDB(db); err != nil {
		return fmt.Errorf("failed to reset database: %v", err)
	}

	return db.Transaction(func(tx *gorm.DB) error {
		// Load test words from test_word.json
		if err := loadTestWords(tx); err != nil {
			return fmt.Errorf("failed to load test words: %v", err)
		}

		// Load test study activities
		if err := loadTestStudyActivities(tx); err != nil {
			return fmt.Errorf("failed to load test study activities: %v", err)
		}

		return nil
	})
}

func loadTestWords(tx *gorm.DB) error {
	jsonFile := "test_word.json"
	content, err := os.ReadFile(jsonFile)
	if err != nil {
		return fmt.Errorf("could not read %s: %v", jsonFile, err)
	}

	var words []models.Word
	if err := json.Unmarshal(content, &words); err != nil {
		return fmt.Errorf("failed to parse %s: %v", jsonFile, err)
	}

	for _, word := range words {
		if err := tx.Create(&word).Error; err != nil {
			return fmt.Errorf("failed to create test word %s: %v", word.Hangul, err)
		}
	}

	return nil
}

func loadTestStudyActivities(tx *gorm.DB) error {
	jsonFile := "test_study_activities.json"
	content, err := os.ReadFile(jsonFile)
	if err != nil {
		return fmt.Errorf("could not read %s: %v", jsonFile, err)
	}

	var activities []models.StudyActivity
	if err := json.Unmarshal(content, &activities); err != nil {
		return fmt.Errorf("failed to parse %s: %v", jsonFile, err)
	}

	for _, activity := range activities {
		if err := tx.Create(&activity).Error; err != nil {
			return fmt.Errorf("failed to create test study activity %s: %v", activity.Name, err)
		}
	}

	return nil
}

func setupTestData(db *gorm.DB) (*TestData, error) {
	// Reset and seed database
	if err := database.SeedTestDB(db); err != nil {
		return nil, fmt.Errorf("failed to seed test database: %v", err)
	}

	// Get the test word from test_word.json data
	var testWord models.Word
	if err := db.Preload("Translations").
		Preload("Sentences").
		Where("hangul = ?", "거").
		First(&testWord).Error; err != nil {
		return nil, fmt.Errorf("failed to get test word: %v", err)
	}

	// ... rest of setup ...

	return &TestData{
		TestWord1: &testWord,
		// ... other fields ...
	}, nil
}
