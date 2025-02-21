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
	ID           uint   `gorm:"primarykey"`
	GROUP_WordID uint   `json:"group_word_id"` // Foreign key for GROUP_Word
	English      string `json:"english"`
}

type JSONWord struct {
	Hangul       string      `json:"hangul"`
	Romanization string      `json:"romanization"`
	English      interface{} `json:"english"`
}

type WordGroup struct {
	gorm.Model
	Name        string       `json:"name"`
	Description string       `json:"description"`
	Words       []GROUP_Word `json:"words"`
	WordsCount  int
}

// Adjust struct to match your actual database schema
type GROUP_Word struct {
	ID          uint `gorm:"primarykey"`
	WordGroupID uint `gorm:"column:word_group_id"`
	// These will be updated based on checkDBSchema findings
	Hangul              string `json:"hangul"`
	Romanization        string `json:"romanization"`
	EnglishTranslations []GROUP_Translation
}

// TableName sets the table name for this model
func (GROUP_Word) TableName() string {
	return "group_words"
}

// Define a separate type for JSON unmarshaling
type JSONGroupData struct {
	Description string     `json:"description"`
	Words       []JSONWord `json:"words"`
}

type JSONGroups struct {
	Groups map[string]JSONGroupData `json:"groups"`
}

func SeedDatabase(db *gorm.DB, jsonFile string) error {
	// Check the database schema to understand the actual column names
	columnMap, err := checkDBSchema(db)
	if err != nil {
		return fmt.Errorf("error checking database schema: %w", err)
	}

	// Update our struct mappings based on schema check
	hangulColumn := "hangul"    // default
	romColumn := "romanization" // default

	if hangulCol, ok := columnMap["hangul"]; ok {
		log.Printf("Found column mapping for 'hangul': %s", hangulCol)
		hangulColumn = hangulCol
	} else {
		// Try to find a likely column for hangul
		for col := range columnMap {
			// Look for columns that might store Korean text
			if col == "korean" || col == "original" || col == "text" || col == "word" {
				log.Printf("Using column '%s' for hangul", col)
				hangulColumn = col
				break
			}
		}
	}

	if romCol, ok := columnMap["romanization"]; ok {
		log.Printf("Found column mapping for 'romanization': %s", romCol)
		romColumn = romCol
	} else {
		// Try to find a likely column for romanization
		for col := range columnMap {
			// Look for columns that might store romanization
			if col == "romanized" || col == "rom" || col == "phonetic" {
				log.Printf("Using column '%s' for romanization", col)
				romColumn = col
				break
			}
		}
	}

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
			Words:       []GROUP_Word{},
		}

		// Create the word group first
		result := db.Create(&wordGroup)
		if result.Error != nil {
			return fmt.Errorf("error creating word group: %w", result.Error)
		}

		// Keep track of words for logging
		wordCount := 0

		// Iterate through the words
		for _, jsonWord := range groupData.Words {
			// Skip words if the group has no data to avoid errors
			if len(jsonWord.Hangul) == 0 {
				continue
			}

			// Use the dynamic SQL approach to insert directly with the correct column names
			sqlStmt := fmt.Sprintf("INSERT INTO group_words (word_group_id, %s, %s) VALUES (?, ?, ?)",
				hangulColumn, romColumn)

			result := db.Exec(sqlStmt, wordGroup.ID, jsonWord.Hangul, jsonWord.Romanization)
			if result.Error != nil {
				return fmt.Errorf("error creating word: %w", result.Error)
			}

			// Get the ID of the inserted word
			var wordID uint
			db.Raw("SELECT last_insert_rowid()").Scan(&wordID)
			wordCount++

			// Process the English field based on type
			switch englishValue := jsonWord.English.(type) {
			case string:
				// Single string translation
				translation := GROUP_Translation{
					GROUP_WordID: wordID,
					English:      englishValue,
				}

				// Save the translation
				result := db.Create(&translation)
				if result.Error != nil {
					return fmt.Errorf("error creating translation: %w", result.Error)
				}

			case []interface{}:
				// Multiple string translations
				for _, item := range englishValue {
					if str, ok := item.(string); ok {
						translation := GROUP_Translation{
							GROUP_WordID: wordID,
							English:      str,
						}

						// Save the translation
						result := db.Create(&translation)
						if result.Error != nil {
							return fmt.Errorf("error creating translation: %w", result.Error)
						}
					} else {
						log.Printf("Warning: Invalid English translation type for %s", jsonWord.Hangul)
					}
				}
			default:
				log.Printf("Warning: Unexpected English translation format for %s: %T", jsonWord.Hangul, jsonWord.English)
			}
		}

		log.Printf("Created WordGroup: %s with %d words", wordGroup.Name, wordCount)
	}

	return nil
}

// Structure to hold column information from SQLite
type sqliteColumn struct {
	CID       int
	Name      string
	Type      string
	NotNull   bool
	DfltValue interface{}
	PK        int // Changed to int to match the database's integer type
}

// Function to check the database schema and get column information
func checkDBSchema(db *gorm.DB) (map[string]string, error) {
	// For SQLite3, we can use PRAGMA table_info
	var columns []sqliteColumn
	result := db.Raw("PRAGMA table_info(group_words)").Scan(&columns)
	if result.Error != nil {
		return nil, fmt.Errorf("error getting table schema: %w", result.Error)
	}

	// Log all columns to help with debugging
	log.Println("Group_words table schema:")
	columnMap := make(map[string]string)

	for _, col := range columns {
		// Convert integer to boolean for logging purposes
		isPrimaryKey := col.PK != 0
		log.Printf("Column: %s, Type: %s, PK: %v", col.Name, col.Type, isPrimaryKey)
		columnMap[col.Name] = col.Name
	}

	// If no columns found, that's an error
	if len(columns) == 0 {
		return nil, fmt.Errorf("no columns found in group_words table, check if table exists")
	}

	return columnMap, nil
}
