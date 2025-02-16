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
	Hangul       string   `json:"hangul"`
	Romanization string   `json:"romanization"`
	English      []string `json:"english"`
	Type         string   `json:"type"`
	Example      struct {
		Korean  string `json:"korean"`
		English string `json:"english"`
	} `json:"example"`
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
			Hangul:         wordData.Hangul,
			Romanization:   wordData.Romanization,
			English:        wordData.English,
			Type:           wordData.Type,
			ExampleKorean:  wordData.Example.Korean,
			ExampleEnglish: wordData.Example.English,
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
