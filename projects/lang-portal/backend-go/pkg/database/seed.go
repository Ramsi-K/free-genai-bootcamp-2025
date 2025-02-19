package database

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"

	"github.com/Ramsi-K/free-genai-bootcamp-2025/projects/lang-portal/backend-go/internal/models"

	"gorm.io/gorm"
)

type WordData struct {
	Hangul          string   `json:"hangul"`
	Romanization    string   `json:"romanization"`
	Type            string   `json:"type"`
	English         []string `json:"english"`
	ExampleSentence struct {
		Korean  string `json:"korean"`
		English string `json:"english"`
	} `json:"example_sentence"`
}

type WordGroupMapping struct {
	Hangul     string   `json:"hangul"`
	GroupNames []string `json:"group_names"`
}

// LoadSeedData is the main entry point for seeding the database
func LoadSeedData(db *gorm.DB) error {
	// Get the current working directory
	cwd, err := os.Getwd()
	if err != nil {
		return fmt.Errorf("failed to get working directory: %v", err)
	}

	// Use the seed directory relative to the current working directory
	dataDir := filepath.Join(cwd, "seed")

	// Call SeedDatabase with the data directory
	return SeedDatabase(db, dataDir)
}

// SeedDatabase handles the actual seeding process
func SeedDatabase(db *gorm.DB, dataDir string) error {
	// Begin transaction
	tx := db.Begin()
	if tx.Error != nil {
		return tx.Error
	}

	// Clean existing data
	if err := cleanDatabase(tx); err != nil {
		tx.Rollback()
		return err
	}

	// Load and seed words
	words, err := loadWords(dataDir)
	if err != nil {
		tx.Rollback()
		return fmt.Errorf("failed to load words: %v", err)
	}

	// Create words
	for _, wordData := range words {
		word := models.Word{
			Hangul:       wordData.Hangul,
			Romanization: wordData.Romanization,
			Type:         wordData.Type,
			English:      wordData.English,
			ExampleSentence: models.Example{
				Korean:  wordData.ExampleSentence.Korean,
				English: wordData.ExampleSentence.English,
			},
		}

		if err := tx.Create(&word).Error; err != nil {
			tx.Rollback()
			return fmt.Errorf("failed to create word %s: %v", word.Hangul, err)
		}
	}

	// Load word-group mappings to create unique groups
	mappings, err := loadWordGroupMappings(dataDir)
	if err != nil {
		tx.Rollback()
		return fmt.Errorf("failed to load word-group mappings: %v", err)
	}

	// Create unique groups from mappings
	uniqueGroups := make(map[string]int)
	for _, mapping := range mappings {
		for _, groupName := range mapping.GroupNames {
			uniqueGroups[groupName]++
		}
	}

	// Create groups with word counts
	for groupName, count := range uniqueGroups {
		group := models.Group{
			Name:       groupName,
			WordsCount: count,
		}
		if err := tx.Create(&group).Error; err != nil {
			tx.Rollback()
			return fmt.Errorf("failed to create group %s: %v", groupName, err)
		}
	}

	// Create default study activities
	activities := []models.StudyActivity{
		{
			Name:         "Flashcards",
			Description:  "Practice words with flashcards",
			Type:         "flashcards",
			ThumbnailURL: "/images/flashcards.png",
			URL:          "http://localhost:8080/study-activities/flashcards",
		},
		{
			Name:         "Multiple Choice",
			Description:  "Test your knowledge with multiple choice questions",
			Type:         "multiple_choice",
			ThumbnailURL: "/images/multiple_choice.png",
			URL:          "http://localhost:8080/study-activities/multiple-choice",
		},
		{
			Name:         "Sentence Practice",
			Description:  "Practice using words in sentences",
			Type:         "sentence_practice",
			ThumbnailURL: "/images/sentence_practice.png",
			URL:          "http://localhost:8080/study-activities/sentence-practice",
		},
	}

	for _, activity := range activities {
		if err := tx.Create(&activity).Error; err != nil {
			tx.Rollback()
			return fmt.Errorf("failed to create activity %s: %v", activity.Name, err)
		}
	}

	return tx.Commit().Error
}

func cleanDatabase(tx *gorm.DB) error {
	// Clean up tables using Unscoped() to permanently delete rows
	models := []interface{}{
		&models.Word{},
		&models.Group{},
		&models.StudyActivity{},
		&models.StudySession{},
		&models.WordReview{},
		&models.SentencePracticeAttempt{},
	}

	for _, model := range models {
		if err := tx.Session(&gorm.Session{AllowGlobalUpdate: true}).Unscoped().Delete(model).Error; err != nil {
			return err
		}
	}
	return nil
}

func loadWords(dataDir string) ([]WordData, error) {
	file, err := os.ReadFile(filepath.Join(dataDir, "data_korean.json"))
	if err != nil {
		return nil, fmt.Errorf("error reading data_korean.json: %v", err)
	}

	var words []WordData
	if err := json.Unmarshal(file, &words); err != nil {
		return nil, fmt.Errorf("error unmarshaling data_korean.json: %v", err)
	}

	return words, nil
}

func loadWordGroupMappings(dataDir string) ([]WordGroupMapping, error) {
	file, err := os.ReadFile(filepath.Join(dataDir, "word_groups.json"))
	if err != nil {
		return nil, fmt.Errorf("error reading word_groups.json: %v", err)
	}

	var mappings []WordGroupMapping
	if err := json.Unmarshal(file, &mappings); err != nil {
		return nil, fmt.Errorf("error unmarshaling word_groups.json: %v", err)
	}

	return mappings, nil
}

// SeedTestData inserts test data into the database
func SeedTestData(db *gorm.DB) error {
	// Create test words
	words := []models.Word{
		{
			Hangul:       "학교",
			Romanization: "hakgyo",
			English:      []string{"school"},
			Type:         "noun",
			ExampleSentence: models.Example{
				Korean:  "나는 학교에 갑니다",
				English: "I go to school",
			},
		},
		{
			Hangul:       "사과",
			Romanization: "sagwa",
			English:      []string{"apple"},
			Type:         "noun",
			ExampleSentence: models.Example{
				Korean:  "사과를 먹습니다",
				English: "I eat an apple",
			},
		},
	}

	// Insert words into database
	for _, word := range words {
		if err := db.Create(&word).Error; err != nil {
			return err
		}
	}

	// Create test groups
	groups := []models.Group{
		{Name: "School"},
		{Name: "Food"},
	}

	// Insert groups into database
	for _, group := range groups {
		if err := db.Create(&group).Error; err != nil {
			return err
		}
	}

	return nil
}
