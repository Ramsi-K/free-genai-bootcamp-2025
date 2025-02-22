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

	// ✅ Load only test-specific data instead of full word_groups.json
	log.Println("🌱 Seeding test database with controlled test data...")
	err = models.SeedDatabase(db, "test_word_groups.json") // ✅ Controlled test data
	if err != nil {
		log.Printf("⚠️ Error seeding test DB: %v", err)
		return err
	}

	// ✅ Add test study session so those tests don't fail
	_, err = createTestStudySession(db, 1, 1, true)
	if err != nil {
		log.Printf("⚠️ Error creating test study session: %v", err)
		return err
	}

	log.Println("✅ Test database reset successfully!")
	return nil
}

// Example for createTestWord in test_utils.go
func createTestWord(db *gorm.DB, hangul string) (*models.Word, error) {
	// Add a unique timestamp to ensure uniqueness
	uniqueHangul := fmt.Sprintf("%s_%d", hangul, time.Now().UnixNano())

	// Create the word
	word := &models.Word{
		Hangul:       uniqueHangul,
		Romanization: "test",
		Type:         "noun",
	}

	result := db.Create(word)
	if result.Error != nil {
		log.Printf("Error creating word: %v", result.Error)
		return nil, result.Error
	}

	// Create a translation
	translation := &models.Translation{
		WordID:  word.ID,
		Hangul:  hangul,
		English: "test translation",
	}

	if err := db.Create(translation).Error; err != nil {
		log.Printf("Error creating translation: %v", err)
		return nil, err
	}

	// Create a sentence
	sentence := &models.Sentence{
		WordID:  word.ID,
		Korean:  uniqueHangul + " 문장",
		English: "Test sentence for " + uniqueHangul,
	}

	if err := db.Create(sentence).Error; err != nil {
		log.Printf("Error creating sentence: %v", err)
		return nil, err
	}

	// Reload the word with associations
	var reloadedWord models.Word
	if err := db.Preload("EnglishTranslations").Preload("Sentences").First(&reloadedWord, word.ID).Error; err != nil {
		log.Printf("Error reloading word: %v", err)
		return nil, err
	}

	return &reloadedWord, nil
}

// createTestGroup creates a test word group and associates each provided word
// by creating a new GROUP_Word record from the given word's Hangul and Romanization.
// createTestGroup creates a test word group and associates each provided word
// by inserting a new GROUP_Word record using (word_group_id, hangul, romanization).
func createTestGroup(db *gorm.DB, name string, words []models.Word) (*models.WordGroup, error) {
	// Create group with a default description.
	group := &models.WordGroup{
		Name:        name,
		Description: "Test Description",
		WordsCount:  0,
	}
	if err := db.Create(group).Error; err != nil {
		return nil, fmt.Errorf("failed to create group: %w", err)
	}

	// Get the actual columns in group_words table
	rows, err := db.Raw("PRAGMA table_info(group_words)").Rows()
	if err != nil {
		return nil, fmt.Errorf("failed to get table schema: %w", err)
	}
	defer rows.Close()
	columnMap := make(map[string]bool)
	type Column struct {
		CID       int
		Name      string
		Type      string
		NotNull   int
		DfltValue any
		PK        int
	}
	for rows.Next() {
		var col Column
		if err := rows.Scan(&col.CID, &col.Name, &col.Type, &col.NotNull, &col.DfltValue, &col.PK); err != nil {
			return nil, fmt.Errorf("failed to scan column: %w", err)
		}
		columnMap[col.Name] = true
	}

	// For each word provided, create a GROUP_Word record.
	for _, word := range words {
		var query string
		var args []any
		// New join table design: we expect columns "word_group_id", "hangul", "romanization"
		if columnMap["word_group_id"] && columnMap["hangul"] && columnMap["romanization"] {
			query = "INSERT INTO group_words (word_group_id, hangul, romanization) VALUES (?, ?, ?)"
			args = []any{group.ID, word.Hangul, word.Romanization}
		} else {
			return nil, fmt.Errorf("cannot determine group_words table schema")
		}
		if err := db.Exec(query, args...).Error; err != nil {
			return nil, fmt.Errorf("failed to associate word with group: %w", err)
		}
		group.WordsCount++
	}

	// Update group record with the correct word count.
	if err := db.Model(group).Update("WordsCount", group.WordsCount).Error; err != nil {
		return nil, fmt.Errorf("failed to update group count: %w", err)
	}
	return group, nil
}

// // createTestGroup creates a test word group
// func createTestGroup(db *gorm.DB, name string, words []models.Word) (*models.WordGroup, error) {
// 	// Check if group already exists
// 	var existingGroup models.WordGroup
// 	if err := db.Where("name = ?", name).First(&existingGroup).Error; err == nil {
// 		return &existingGroup, nil
// 	}

// 	// Create group
// 	group := &models.WordGroup{
// 		Name:        name,
// 		Description: "Test Description",
// 		WordsCount:  len(words),
// 	}

// 	if err := db.Create(group).Error; err != nil {
// 		return nil, fmt.Errorf("failed to create group: %w", err)
// 	}

// 	// Associate words if provided
// 	if len(words) > 0 {
// 		// First check what columns actually exist in the group_words table
// 		// var columns []string
// 		rows, err := db.Raw("PRAGMA table_info(group_words)").Rows()
// 		if err != nil {
// 			return nil, fmt.Errorf("failed to get table schema: %w", err)
// 		}
// 		defer rows.Close()

// 		type Column struct {
// 			CID       int
// 			Name      string
// 			Type      string
// 			NotNull   int
// 			DfltValue any
// 			PK        int
// 		}

// 		columnMap := make(map[string]bool)
// 		for rows.Next() {
// 			var col Column
// 			if err := rows.Scan(&col.CID, &col.Name, &col.Type, &col.NotNull, &col.DfltValue, &col.PK); err != nil {
// 				return nil, fmt.Errorf("failed to scan column: %w", err)
// 			}
// 			columnMap[col.Name] = true
// 		}

// 		// Create the SQL based on actual column names
// 		for _, word := range words {
// 			var query string
// 			var args []any

// 			if columnMap["word_id"] && columnMap["word_group_id"] {
// 				query = "INSERT INTO group_words (word_group_id, word_id) VALUES (?, ?)"
// 				args = []any{group.ID, word.ID}
// 			} else if columnMap["word_id"] && columnMap["group_id"] {
// 				query = "INSERT INTO group_words (group_id, word_id) VALUES (?, ?)"
// 				args = []any{group.ID, word.ID}
// 			} else if columnMap["WordGroupID"] && columnMap["WordID"] {
// 				query = "INSERT INTO group_words (WordGroupID, WordID) VALUES (?, ?)"
// 				args = []any{group.ID, word.ID}
// 			} else {
// 				// If none of the expected column combinations exist, return error
// 				return nil, fmt.Errorf("cannot determine group_words table schema")
// 			}

// 			if err := db.Exec(query, args...).Error; err != nil {
// 				return nil, fmt.Errorf("failed to associate word with group: %w", err)
// 			}
// 		}
// 	}

// 	return group, nil
// }

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
