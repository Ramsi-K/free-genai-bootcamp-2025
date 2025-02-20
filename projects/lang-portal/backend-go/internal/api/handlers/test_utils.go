package handlers

import (
	"encoding/json"
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

const testDBName = "test.db"

// getSeedFilePath returns the absolute path to a seed file
func getSeedFilePath(filename string) string {
	// Try different possible locations
	possiblePaths := []string{
		fmt.Sprintf("seed/%s", filename),
		fmt.Sprintf("../../seed/%s", filename),
		fmt.Sprintf("../../../seed/%s", filename),
	}

	for _, path := range possiblePaths {
		if _, err := os.Stat(path); err == nil {
			return path
		}
	}
	return filename // Return original as fallback
}

// setupTestDB initializes the test database
func setupTestDB() (*gorm.DB, error) {
	newLogger := logger.New(
		log.New(os.Stdout, "\r\n", log.LstdFlags), // io writer
		logger.Config{
			SlowThreshold: time.Second,   // Slow SQL threshold
			LogLevel:      logger.Silent, // Log level
			Colorful:      false,         // Disable color
		},
	)

	db, err := gorm.Open(sqlite.Open(testDBName), &gorm.Config{
		Logger: newLogger,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to open database: %w", err)
	}

	// AutoMigrate will create tables, add missing columns, create indexes,
	// and constrain foreign keys
	err = db.AutoMigrate(&models.Word{}, &models.Translation{}, &models.Sentence{})
	if err != nil {
		return nil, fmt.Errorf("failed to automigrate database: %w", err)
	}

	return db, nil
}

// setupTestDBWithSeedData creates a test database and loads seed data
func setupTestDBWithSeedData() (*gorm.DB, error) {
	db, err := setupTestDB()
	if err != nil {
		return nil, err
	}

	// Load seed data
	if err := loadSeedData(db); err != nil {
		log.Printf("Warning: Error loading seed data: %v", err)
	}

	return db, nil
}

// loadSeedData loads initial data from JSON files
func loadSeedData(db *gorm.DB) error {
	if err := loadWordGroups(db); err != nil {
		log.Printf("Warning: Could not load word groups: %v", err)
		// Create default group if loading word groups fails
		if err := createDefaultGroup(db); err != nil {
			return fmt.Errorf("failed to create default group: %v", err)
		}
	}

	return nil
}

// loadWordGroups loads word groups data from JSON file
func loadWordGroups(db *gorm.DB) error {
	wordGroupsPath := getSeedFilePath("word_groups.json")
	wordGroupsData, err := os.ReadFile(wordGroupsPath)
	if err != nil {
		return fmt.Errorf("could not read word_groups.json: %v", err)
	}

	var wordGroupsMap struct {
		Groups map[string]struct {
			Description string `json:"description"`
			Words       []struct {
				Hangul       string   `json:"hangul"`
				Romanization string   `json:"romanization"`
				English      []string `json:"english"`
			} `json:"words"`
		} `json:"groups"`
	}

	if err := json.Unmarshal(wordGroupsData, &wordGroupsMap); err != nil {
		return fmt.Errorf("could not parse word_groups.json: %v", err)
	}

	// Create word groups and their words
	for groupName, groupData := range wordGroupsMap.Groups {
		group := &models.WordGroup{
			Name:        groupName,
			Description: groupData.Description,
			WordsCount:  len(groupData.Words),
		}

		if err := db.Create(group).Error; err != nil {
			log.Printf("Warning: Failed to create group %s: %v", groupName, err)
			continue
		}

		// Create words for this group
		for _, wordData := range groupData.Words {
			translations := make([]models.Translation, len(wordData.English))
			for i, eng := range wordData.English {
				translations[i] = models.Translation{
					English: eng,
				}
			}

			sentence := models.Sentence{
				Korean:  "테스트 문장입니다.",
				English: "This is a test sentence.",
			}

			word := &models.Word{
				Hangul:              wordData.Hangul,
				Romanization:        wordData.Romanization,
				EnglishTranslations: translations,
				Type:                "noun",
				Sentences:           []models.Sentence{sentence},
				CorrectCount:        0,
				WrongCount:          0,
			}

			if err := db.Create(word).Error; err != nil {
				log.Printf("Warning: Failed to create word %s: %v", wordData.Hangul, err)
				continue
			}

			if err := db.Model(group).Association("Words").Append(word); err != nil {
				log.Printf("Warning: Failed to associate word %s with group %s: %v", wordData.Hangul, groupName, err)
			}
		}
	}

	return nil
}

// createDefaultGroup creates a default word group
func createDefaultGroup(db *gorm.DB) error {
	group := &models.WordGroup{
		Name:        "Test Group",
		Description: "Test Description",
		WordsCount:  0,
	}
	if err := db.Create(group).Error; err != nil {
		return fmt.Errorf("failed to create default group: %v", err)
	}
	return nil
}

// cleanupTestDB closes the database and removes the test database file
func cleanupTestDB(db *gorm.DB) error {
	sqlDB, err := db.DB()
	if err != nil {
		return fmt.Errorf("failed to get sql db: %w", err)
	}
	if err := sqlDB.Close(); err != nil {
		return fmt.Errorf("failed to close database: %w", err)
	}
	if err := os.Remove(testDBName); err != nil {
		return fmt.Errorf("failed to remove test database file: %w", err)
	}
	return nil
}

// createTestGroup creates a test word group with optional words
func createTestGroup(db *gorm.DB, name string, words []models.Word) (*models.WordGroup, error) {
	// First check if group exists
	var existingGroup models.WordGroup
	if err := db.Where("name = ?", name).First(&existingGroup).Error; err == nil {
		return &existingGroup, nil
	}

	group := &models.WordGroup{
		Name:        name,
		Description: "Test Description",
		WordsCount:  len(words),
	}

	if err := db.Create(group).Error; err != nil {
		return nil, err
	}

	if len(words) > 0 {
		if err := db.Model(group).Association("Words").Replace(words); err != nil {
			return nil, err
		}

		// Update WordsCount after creating associations
		var count int64
		if err := db.Model(&models.Word{}).
			Joins("JOIN group_words ON group_words.word_id = words.id").
			Where("group_words.word_group_id = ?", group.ID).
			Count(&count).Error; err != nil {
			return nil, fmt.Errorf("failed to count words: %v", err)
		}

		group.WordsCount = int(count)
		if err := db.Save(group).Error; err != nil {
			return nil, fmt.Errorf("failed to update word count: %v", err)
		}
	}

	return group, nil
}

type SentenceData struct {
	Korean  string `json:"korean"`
	English string `json:"english"`
}

type WordData struct {
	Hangul       string       `json:"hangul"`
	Romanization string       `json:"romanization"`
	English      []string     `json:"english"`
	Type         string       `json:"type"`
	Sentence     SentenceData `json:"sentence"`
	CorrectCount int          `json:"correct_count"`
	WrongCount   int          `json:"wrong_count"`
}

func createTestWord(db *gorm.DB, hangul string) (*models.Word, error) {
	wordData := WordData{
		Hangul:       hangul,
		Romanization: "test",
		English:      []string{"test"},
		Type:         "noun",
		Sentence: SentenceData{
			Korean:  "테스트 문장입니다.",
			English: "This is a test sentence.",
		},
		CorrectCount: 0,
		WrongCount:   0,
	}

	translations := make([]models.Translation, len(wordData.English))
	for i, eng := range wordData.English {
		translations[i] = models.Translation{
			English: eng,
		}
	}

	sentence := models.Sentence{
		Korean:  wordData.Sentence.Korean,
		English: wordData.Sentence.English,
	}

	word := &models.Word{
		Hangul:              wordData.Hangul,
		Romanization:        wordData.Romanization,
		EnglishTranslations: translations,
		Type:                wordData.Type,
		Sentences:           []models.Sentence{sentence},
		CorrectCount:        wordData.CorrectCount,
		WrongCount:          wordData.WrongCount,
	}

	result := db.Create(word)
	if result.Error != nil {
		return nil, fmt.Errorf("failed to create test word: %w", result.Error)
	}

	return word, nil
}

// createTestActivity creates a test study activity
func createTestActivity(db *gorm.DB, name string) (*models.StudyActivity, error) {
	activity := &models.StudyActivity{
		Name:        name,
		Description: "Test Description",
		Type:        "test",
		Thumbnail:   "/test.png",
		LaunchURL:   "/test",
	}

	if err := db.Create(activity).Error; err != nil {
		return nil, err
	}

	return activity, nil
}

// createTestStudySession creates a test study session
func createTestStudySession(db *gorm.DB, wordID uint, correct bool) error {
	studySession := models.StudySession{
		WordID:  wordID,
		Correct: correct,
	}
	return db.Create(&studySession).Error
}

// resetTestDB drops all tables and recreates them
func resetTestDB(db *gorm.DB) error {
	// Drop all tables in correct order to avoid foreign key constraints
	if err := db.Migrator().DropTable(
		&models.StudySession{},
		&models.WordReviewItem{},
		"group_words", // Drop join table first
		&models.Word{},
		&models.WordGroup{},
		&models.StudyActivity{},
		&models.Translation{},
		&models.Sentence{},
	); err != nil {
		return fmt.Errorf("failed to drop tables: %v", err)
	}
	err := db.AutoMigrate(&models.Word{}, &models.Translation{}, &models.Sentence{})
	if err != nil {
		return fmt.Errorf("failed to automigrate database: %w", err)
	}
	return nil
}

// resetTestDBWithSeedData resets the database and reloads seed data
func resetTestDBWithSeedData(db *gorm.DB) error {
	if err := resetTestDB(db); err != nil {
		return err
	}

	// Reload seed data
	if err := loadSeedData(db); err != nil {
		return fmt.Errorf("failed to reload seed data: %v", err)
	}

	return nil
}

// withCleanDB wraps a test function with database cleanup
func withCleanDB(t *testing.T, db *gorm.DB, testFunc func()) {
	// Reset before test
	if err := resetTestDB(db); err != nil {
		t.Fatalf("Failed to reset test database before test: %v", err)
	}

	// Run the test
	testFunc()

	// Reset after test
	if err := resetTestDB(db); err != nil {
		t.Fatalf("Failed to reset test database after test: %v", err)
	}
}
