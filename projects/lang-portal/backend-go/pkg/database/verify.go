package database

import (
	"fmt"

	"github.com/Ramsi-K/free-genai-bootcamp-2025/projects/lang-portal/backend-go/internal/models"

	"gorm.io/gorm"
)

func VerifyData(db *gorm.DB) error {
	var wordCount int64
	if err := db.Model(&models.Word{}).Count(&wordCount).Error; err != nil {
		return fmt.Errorf("failed to count words: %v", err)
	}

	var groupCount int64
	if err := db.Model(&models.Group{}).Count(&groupCount).Error; err != nil {
		return fmt.Errorf("failed to count groups: %v", err)
	}

	fmt.Printf("Database contains %d words and %d groups\n", wordCount, groupCount)

	// Print sample word
	var word models.Word
	if err := db.First(&word).Error; err != nil {
		return fmt.Errorf("failed to fetch sample word: %v", err)
	}

	fmt.Printf("\nSample word:\n")
	fmt.Printf("Hangul: %s\n", word.Hangul)
	fmt.Printf("English: %v\n", word.English)
	fmt.Printf("Type: %s\n", word.Type)

	return nil
}
