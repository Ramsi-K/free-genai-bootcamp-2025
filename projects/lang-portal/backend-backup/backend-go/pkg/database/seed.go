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

// LoadSeedData is the main entry point for seeding the database
func LoadSeedData(db *gorm.DB) error {
	// Create Core Korean group
	group := models.Group{
		Name: "Core Korean",
	}
	if err := db.FirstOrCreate(&group, models.Group{Name: "Core Korean"}).Error; err != nil {
		return fmt.Errorf("failed to create core group: %v", err)
	}

	// Read and parse words data using absolute path
	wordFilePath := filepath.Join("seed", "data_korean.json")
	absWordFilePath, err := filepath.Abs(wordFilePath)
	if err != nil {
		return fmt.Errorf("error obtaining absolute path for data_korean.json: %v", err)
	}
	data, err := os.ReadFile(absWordFilePath)
	if err != nil {
		return fmt.Errorf("failed to read seed data from %s: %v", absWordFilePath, err)
	}

	var words []WordData
	if err := json.Unmarshal(data, &words); err != nil {
		return fmt.Errorf("failed to parse seed data: %v", err)
	}

	fmt.Printf("Successfully loaded %d words from %s\n", len(words), absWordFilePath)

	// Begin transaction
	tx := db.Begin()
	if tx.Error != nil {
		return fmt.Errorf("failed to begin transaction: %v", tx.Error)
	}

	// Insert words using correct JSON field 'Example'
	for _, wordData := range words {
		word := models.Word{
			Hangul:       wordData.Hangul,
			Romanization: wordData.Romanization,
			English:      wordData.English,
			Type:         wordData.Type,
			ExampleSentence: models.Example{
				Korean:  wordData.ExampleSentence.Korean,
				English: wordData.ExampleSentence.English,
			},
		}

		if err := tx.Create(&word).Error; err != nil {
			tx.Rollback()
			return fmt.Errorf("failed to create word: %v", err)
		}
	}

	return tx.Commit().Error
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
	wordPath := filepath.Join(dataDir, "data_korean.json")
	absPath, err := filepath.Abs(wordPath)
	if err != nil {
		return nil, fmt.Errorf("error obtaining absolute path for data_korean.json: %v", err)
	}
	file, err := os.ReadFile(absPath)
	if err != nil {
		return nil, fmt.Errorf("error reading data_korean.json from %s: %v", absPath, err)
	}

	var words []WordData
	if err := json.Unmarshal(file, &words); err != nil {
		return nil, fmt.Errorf("error unmarshaling data_korean.json: %v", err)
	}

	fmt.Printf("Successfully loaded %d words from %s\n", len(words), absPath)
	return words, nil
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

	return nil
}
