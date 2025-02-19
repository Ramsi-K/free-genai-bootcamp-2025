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

// setupTestDB creates an in-memory SQLite database for testing
func setupTestDB() (*gorm.DB, error) {
	db, err := gorm.Open(sqlite.Open(":memory:"), &gorm.Config{
		Logger: logger.Default.LogMode(logger.Silent),
		// Disable foreign key checks during resets
		DisableForeignKeyConstraintWhenMigrating: true,
	})
	if err != nil {
		return nil, err
	}

	// Run initial migrations
	if err := resetTestDB(db); err != nil {
		return nil, err
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
	// Load word groups data
	wordGroupsPath := getSeedFilePath("word_groups.json")
	wordGroupsData, err := os.ReadFile(wordGroupsPath)
	if err != nil {
		log.Printf("Warning: Could not read word_groups.json: %v", err)
		// Create default group if file not found
		group := &models.WordGroup{
			Name:        "Test Group",
			Description: "Test Description",
			WordsCount:  0,
		}
		if err := db.Create(group).Error; err != nil {
			return fmt.Errorf("failed to create default group: %v", err)
		}
	} else {
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
			log.Printf("Warning: Could not parse word_groups.json: %v", err)
		} else {
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
					word := &models.Word{
						Hangul:       wordData.Hangul,
						Romanization: wordData.Romanization,
						English:      models.StringSlice(wordData.English),
						Type:         "noun",
						ExampleSentence: models.ExampleSentence{
							Korean:  "테스트 문장입니다.",
							English: "This is a test sentence.",
						},
						StudyStatistics: models.StudyStatistics{
							CorrectCount: 0,
							WrongCount:   0,
						},
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
		}
	}

	// Create default study activities if not loaded from file
	activities := []models.StudyActivity{
		{
			Name:        "Flashcards",
			Description: "Practice words with flashcards",
			Type:        "flashcards",
			Thumbnail:   "/images/flashcards.png",
			LaunchURL:   "/study/flashcards",
		},
		{
			Name:        "Multiple Choice",
			Description: "Test your knowledge with multiple choice questions",
			Type:        "quiz",
			Thumbnail:   "/images/quiz.png",
			LaunchURL:   "/study/quiz",
		},
		{
			Name:        "Typing Practice",
			Description: "Practice typing Korean words",
			Type:        "typing",
			Thumbnail:   "/images/typing.png",
			LaunchURL:   "/study/typing",
		},
	}

	for _, activity := range activities {
		if err := db.Where(models.StudyActivity{Name: activity.Name}).
			FirstOrCreate(&activity).Error; err != nil {
			log.Printf("Warning: Failed to create activity %s: %v", activity.Name, err)
		}
	}

	return nil
}

// cleanupTestDB closes the test database connection
func cleanupTestDB(db *gorm.DB) {
	sqlDB, err := db.DB()
	if err == nil {
		sqlDB.Close()
	}
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

// createTestWord creates a test word
func createTestWord(db *gorm.DB, hangul string) (*models.Word, error) {
	word := &models.Word{
		Hangul:       hangul,
		Romanization: "test",
		Type:         "noun",
		CorrectCount: 0,
		WrongCount:   0,
	}

	if err := db.Create(word).Error; err != nil {
		return nil, err
	}

	// Create test translation
	translation := &models.Translation{
		WordID:  word.ID,
		English: "test",
	}
	if err := db.Create(translation).Error; err != nil {
		return nil, err
	}

	// Create test sentence
	sentence := &models.Sentence{
		WordID:  word.ID,
		Korean:  "Test Korean sentence",
		English: "Test English sentence",
	}
	if err := db.Create(sentence).Error; err != nil {
		return nil, err
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
func createTestStudySession(db *gorm.DB, groupID, activityID uint) (*models.StudySession, error) {
	// Verify group exists
	var group models.WordGroup
	if err := db.First(&group, groupID).Error; err != nil {
		return nil, fmt.Errorf("group not found: %v", err)
	}

	// Verify activity exists
	var activity models.StudyActivity
	if err := db.First(&activity, activityID).Error; err != nil {
		return nil, fmt.Errorf("activity not found: %v", err)
	}

	now := time.Now()
	session := &models.StudySession{
		GroupID:      groupID,
		ActivityID:   activityID,
		CorrectCount: 5,
		WrongCount:   2,
		CompletedAt:  now,
		CreatedAt:    now,
		UpdatedAt:    now,
	}

	if err := db.Create(session).Error; err != nil {
		return nil, fmt.Errorf("failed to create study session: %v", err)
	}

	// Update word statistics for words in the group
	var words []models.Word
	if err := db.Model(&group).Association("Words").Find(&words); err != nil {
		return nil, fmt.Errorf("failed to get group words: %v", err)
	}

	for _, word := range words {
		word.StudyStatistics.CorrectCount += 2
		word.StudyStatistics.WrongCount += 1
		if err := db.Save(&word).Error; err != nil {
			return nil, fmt.Errorf("failed to update word statistics: %v", err)
		}
	}

	return session, nil
}

// resetTestDB resets the database to a clean state
func resetTestDB(db *gorm.DB) error {
	// Drop all tables in correct order to avoid foreign key constraints
	if err := db.Migrator().DropTable(
		&models.StudySession{},
		&models.WordReviewItem{},
		"group_words", // Drop join table first
		&models.Word{},
		&models.WordGroup{},
		&models.StudyActivity{},
	); err != nil {
		return fmt.Errorf("failed to drop tables: %v", err)
	}

	// Run migrations
	if err := db.AutoMigrate(
		&models.Word{},
		&models.WordGroup{},
		&models.StudyActivity{},
		&models.StudySession{},
		&models.WordReviewItem{},
	); err != nil {
		return fmt.Errorf("failed to run migrations: %v", err)
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
