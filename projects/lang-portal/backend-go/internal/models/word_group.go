package models

import (
	"encoding/json"
	"fmt"
	"log"
	"os"

	"gorm.io/gorm"
)

// JSON Structure
type GROUP_Translation struct {
	English string `json:"english"`
}

type JSONWord struct {
	Hangul       string              `json:"hangul"`
	Romanization string              `json:"romanization"`
	English      []GROUP_Translation `json:"english"`
}

type WordGroup struct {
	gorm.Model
	Name        string       `json:"name"`
	Description string       `json:"description"`
	Words       []GROUP_Word `json:"words"`
	WordsCount  int
}

type GROUP_Word struct {
	gorm.Model
	WordGroupID         uint
	Hangul              string              `json:"hangul"`
	Romanization        string              `json:"romanization"`
	EnglishTranslations []GROUP_Translation `json:"english"`
}

type JSONGroups struct {
	Groups map[string]WordGroup `json:"groups"`
}

func SeedDatabase(db *gorm.DB, jsonFile string) error {
	// 1. Read the JSON file
	content, err := os.ReadFile(jsonFile)
	if err != nil {
		return fmt.Errorf("error reading JSON file: %w", err)
	}

	// 2. Unmarshal the JSON data
	var jsonData JSONGroups
	err = json.Unmarshal(content, &jsonData)
	if err != nil {
		return fmt.Errorf("error unmarshaling JSON: %w", err)
	}

	// 3. Iterate through the groups
	for groupName, groupData := range jsonData.Groups {
		// Create a WordGroup
		wordGroup := WordGroup{
			Name:        groupName,
			Description: groupData.Description,
		}

		// Iterate through the words
		for _, jsonWord := range groupData.Words {
			// Create a Word
			word := GROUP_Word{
				Hangul:       jsonWord.Hangul,
				Romanization: jsonWord.Romanization,
			}

			// Create Translations
			for _, english := range jsonWord.EnglishTranslations {
				translation := GROUP_Translation{
					English: english.English,
				}
				word.EnglishTranslations = append(word.EnglishTranslations, translation)
			}

			// Append the Word to the WordGroup
			wordGroup.Words = append(wordGroup.Words, word)
		}

		// 4. Save the WordGroup to the database
		result := db.Create(&wordGroup)
		if result.Error != nil {
			return fmt.Errorf("error creating word group: %w", result.Error)
		}
		log.Printf("Created WordGroup: %s", wordGroup.Name)
	}

	return nil
}
