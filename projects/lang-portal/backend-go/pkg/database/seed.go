package database

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"

	"github.com/Ramsi-K/free-genai-bootcamp-2025/tree/main/projects/lang-portal/backend-go/internal/models"

	"gorm.io/gorm"
)

type WordData struct {
	Hangul          string   `json:"hangul"`
	Romanization    string   `json:"romanization"`
	English         []string `json:"english"`
	Type            string   `json:"type"`
	ExampleSentence struct {
		Korean  string `json:"korean"`
		English string `json:"english"`
	} `json:"example_sentence"`
}

func LoadSeedData(db *gorm.DB) error {
	// Create Core Korean group
	group := models.Group{
		Name: "Core Korean",
	}
	if err := db.FirstOrCreate(&group, models.Group{Name: "Core Korean"}).Error; err != nil {
		return fmt.Errorf("failed to create core group: %v", err)
	}

	// Read and parse words data
	data, err := os.ReadFile(filepath.Join("seed", "data_korean.json"))
	if err != nil {
		return fmt.Errorf("failed to read seed data: %v", err)
	}

	var words []WordData
	if err := json.Unmarshal(data, &words); err != nil {
		return fmt.Errorf("failed to parse seed data: %v", err)
	}

	// Begin transaction
	tx := db.Begin()
	if tx.Error != nil {
		return fmt.Errorf("failed to begin transaction: %v", tx.Error)
	}

	// Insert words
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

		// Add word to group
		if err := tx.Model(&group).Association("Words").Append(&word); err != nil {
			tx.Rollback()
			return fmt.Errorf("failed to associate word with group: %v", err)
		}
	}

	// Update group word count
	group.WordsCount = len(words)
	if err := tx.Save(&group).Error; err != nil {
		tx.Rollback()
		return fmt.Errorf("failed to update group word count: %v", err)
	}

	// Commit transaction
	if err := tx.Commit().Error; err != nil {
		return fmt.Errorf("failed to commit transaction: %v", err)
	}

	return nil
}

// SeedWords loads words from a JSON file and inserts them into the database
func SeedWords(db *gorm.DB, filePath string) error {
	// Read JSON file
	data, err := os.ReadFile(filePath)
	if err != nil {
		return err
	}

	// Parse JSON into slice of Word structs
	var words []models.Word
	if err := json.Unmarshal(data, &words); err != nil {
		return err
	}

	// Insert words into database
	for _, word := range words {
		if err := db.Create(&word).Error; err != nil {
			return err
		}
	}

	return nil
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
