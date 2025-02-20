package models

import (
	"encoding/json"
	"fmt"
	"log"

	"gorm.io/gorm"
)

// JSON Structure
type JSONWord struct {
	Hangul       string   `json:"hangul"`
	Romanization string   `json:"romanization"`
	English      []string `json:"english"`
}

type JSONWordGroup struct {
	Description string     `json:"description"`
	Words       []JSONWord `json:"words"`
}

type JSONGroups struct {
	Groups map[string]JSONWordGroup `json:"groups"`
}

func SeedDatabase(db *gorm.DB, jsonFile string) error {
	// 1. Read the JSON file
	content, err := ioutil.ReadFile(jsonFile)
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
		wordGroup := models.WordGroup{
			Name:        groupName,
			Description: groupData.Description,
		}

		// Iterate through the words
		for _, jsonWord := range groupData.Words {
			// Create a Word
			word := models.Word{
				Hangul:       jsonWord.Hangul,
				Romanization: jsonWord.Romanization,
			}

			// Create Translations
			for _, englishTranslation := range jsonWord.English {
				translation := models.Translation{
					English: englishTranslation,
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
