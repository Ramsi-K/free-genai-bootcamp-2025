package handlers

import (
	"fmt"
	"log"
	"os"
	"testing"
	"time"

	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/models"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

// setupTestDB initializes a test database
func setupTestDB() (*gorm.DB, error) {
	// Configure a silent logger for tests
	newLogger := logger.New(
		log.New(os.Stdout, "\r\n", log.LstdFlags),
		logger.Config{
			SlowThreshold: time.Second,
			LogLevel:      logger.Silent, // Silent in tests
			Colorful:      false,
		},
	)

	// Use an in-memory database for tests
	db, err := gorm.Open(sqlite.Open("file::memory:?cache=shared"), &gorm.Config{
		Logger: newLogger,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to open database: %w", err)
	}

	// AutoMigrate all required tables
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
		return nil, fmt.Errorf("failed to automigrate database: %w", err)
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
	// Delete data from all tables in the correct order
	tables := []string{
		"word_review_items",
		"study_sessions",
		"translations",
		"sentences",
		"group_words",
		"group_translations",
		"words",
		"word_groups",
		"study_activities",
	}

	for _, table := range tables {
		// Check if table exists
		if db.Migrator().HasTable(table) {
			if err := db.Exec(fmt.Sprintf("DELETE FROM %s", table)).Error; err != nil {
				// Ignore errors for missing tables
				log.Printf("Warning: Could not clear table %s: %v", table, err)
			}
		}
	}

	return nil
}

// createTestWord creates a test word with translations and a sentence
func createTestWord(db *gorm.DB, hangul string) (*models.Word, error) {
	// Add a unique suffix to ensure uniqueness
	uniqueHangul := fmt.Sprintf("%s-%d", hangul, time.Now().UnixNano())

	// Create the word
	word := &models.Word{
		Hangul:       uniqueHangul,
		Romanization: "test",
		Type:         "noun",
	}

	if err := db.Create(word).Error; err != nil {
		return nil, fmt.Errorf("failed to create word: %w", err)
	}

	// Create a translation
	translation := &models.Translation{
		WordID:    word.ID,
		Hangul:    hangul,
		English:   "test",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	if err := db.Create(translation).Error; err != nil {
		return nil, fmt.Errorf("failed to create translation: %w", err)
	}

	// Create a sentence
	sentence := &models.Sentence{
		WordID:    word.ID,
		Korean:    "테스트 문장입니다.",
		English:   "This is a test sentence.",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	if err := db.Create(sentence).Error; err != nil {
		return nil, fmt.Errorf("failed to create sentence: %w", err)
	}

	// Reload the word with associations
	var wordWithAssociations models.Word
	if err := db.Preload("EnglishTranslations").Preload("Sentences").First(&wordWithAssociations, word.ID).Error; err != nil {
		return nil, fmt.Errorf("failed to reload word: %w", err)
	}

	return &wordWithAssociations, nil
}

// createTestGroup creates a test word group
func createTestGroup(db *gorm.DB, name string, words []models.Word) (*models.WordGroup, error) {
	// Check if group already exists
	var existingGroup models.WordGroup
	if err := db.Where("name = ?", name).First(&existingGroup).Error; err == nil {
		return &existingGroup, nil
	}

	// Create group
	group := &models.WordGroup{
		Name:        name,
		Description: "Test Description",
		WordsCount:  len(words),
	}

	if err := db.Create(group).Error; err != nil {
		return nil, fmt.Errorf("failed to create group: %w", err)
	}

	// Associate words if provided
	if len(words) > 0 {
		// First check what columns actually exist in the group_words table
		// var columns []string
		rows, err := db.Raw("PRAGMA table_info(group_words)").Rows()
		if err != nil {
			return nil, fmt.Errorf("failed to get table schema: %w", err)
		}
		defer rows.Close()

		type Column struct {
			CID       int
			Name      string
			Type      string
			NotNull   int
			DfltValue any
			PK        int
		}

		columnMap := make(map[string]bool)
		for rows.Next() {
			var col Column
			if err := rows.Scan(&col.CID, &col.Name, &col.Type, &col.NotNull, &col.DfltValue, &col.PK); err != nil {
				return nil, fmt.Errorf("failed to scan column: %w", err)
			}
			columnMap[col.Name] = true
		}

		// Create the SQL based on actual column names
		for _, word := range words {
			var query string
			var args []any

			if columnMap["word_id"] && columnMap["word_group_id"] {
				query = "INSERT INTO group_words (word_group_id, word_id) VALUES (?, ?)"
				args = []any{group.ID, word.ID}
			} else if columnMap["word_id"] && columnMap["group_id"] {
				query = "INSERT INTO group_words (group_id, word_id) VALUES (?, ?)"
				args = []any{group.ID, word.ID}
			} else if columnMap["WordGroupID"] && columnMap["WordID"] {
				query = "INSERT INTO group_words (WordGroupID, WordID) VALUES (?, ?)"
				args = []any{group.ID, word.ID}
			} else {
				// If none of the expected column combinations exist, return error
				return nil, fmt.Errorf("cannot determine group_words table schema")
			}

			if err := db.Exec(query, args...).Error; err != nil {
				return nil, fmt.Errorf("failed to associate word with group: %w", err)
			}
		}
	}

	return group, nil
}

// createTestActivity creates a test study activity
func createTestActivity(db *gorm.DB, name string) (*models.StudyActivity, error) {
	// Check if already exists
	var existingActivity models.StudyActivity
	if err := db.Where("name = ?", name).First(&existingActivity).Error; err == nil {
		return &existingActivity, nil
	}

	// Create new activity
	activity := &models.StudyActivity{
		Name:        name,
		Description: "Test Activity Description",
		Type:        "test",
		Thumbnail:   "/images/test.png",
		LaunchURL:   "/activities/test",
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}

	if err := db.Create(activity).Error; err != nil {
		return nil, fmt.Errorf("failed to create activity: %w", err)
	}

	return activity, nil
}

// createTestStudySession creates a test study session
func createTestStudySession(db *gorm.DB, groupID, activityID uint, isCorrect bool) (*models.StudySession, error) {
	session := &models.StudySession{
		StudyActivityID: activityID,
		WordGroupID:     &groupID,
		CorrectCount:    5,
		WrongCount:      2,
		CompletedAt:     time.Now(),
	}

	if isCorrect {
		session.CorrectCount = 1
	} else {
		session.WrongCount = 1
	}

	if err := db.Create(session).Error; err != nil {
		return nil, fmt.Errorf("failed to create study session: %w", err)
	}

	return session, nil
}

// withCleanDB runs a test function with a clean database
func withCleanDB(t *testing.T, db *gorm.DB, testFunc func()) {
	// Reset DB before test
	if err := resetTestDB(db); err != nil {
		t.Fatalf("Failed to reset test database: %v", err)
	}

	// Run the test in a panic-safe environment
	defer func() {
		if r := recover(); r != nil {
			t.Fatalf("Test panicked: %v", r)
		}

		// Reset after test, but don't fail if cleanup fails
		_ = resetTestDB(db)
	}()

	// Run the test
	testFunc()
}
