package database

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"path/filepath"

	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/models"
	"gorm.io/gorm"
)

// KoreanWordData represents the structure of data_korean.json
type KoreanWordData struct {
	Hangul          string   `json:"hangul"`
	Romanization    string   `json:"romanization"`
	Type            string   `json:"type"`
	English         []string `json:"english"`
	ExampleSentence struct {
		Korean  string `json:"korean"`
		English string `json:"english"`
	} `json:"example_sentence"`
}

// StudyActivitySeed represents the structure of study_activities.json
type StudyActivitySeed struct {
	Name         string `json:"name"`
	Description  string `json:"description"`
	Type         string `json:"type"`
	ThumbnailURL string `json:"thumbnail_url"`
	URL          string `json:"url"`
}

type WordGroup struct {
	gorm.Model
	Name        string `json:"name"`
	Description string `json:"description"`
	WordsCount  int
}

type GROUP_Word struct {
	ID           uint   `gorm:"primarykey"`
	WordGroupID  uint   `gorm:"index"`
	Hangul       string `gorm:"type:text"`
	Romanization string `gorm:"type:text"`
}

type GROUP_Translation struct {
	ID           uint   `gorm:"primarykey"`
	GROUP_WordID uint   `gorm:"index"`
	English      string `gorm:"type:text"`
}

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

// loadKoreanWords loads the main vocabulary from data_korean.json
func loadKoreanWords(tx *gorm.DB) error {
	// Load Korean words data
	dataPath := getSeedFilePath("data_korean.json")
	data, err := os.ReadFile(filepath.Clean(dataPath))
	if err != nil {
		return fmt.Errorf("could not read data_korean.json: %v", err)
	}

	var wordsData []KoreanWordData
	if err := json.Unmarshal(data, &wordsData); err != nil {
		return fmt.Errorf("failed to parse data_korean.json: %v", err)
	}

	log.Printf("Loading %d Korean words from data_korean.json", len(wordsData))

	// Create words
	for _, wordData := range wordsData {
		word := &models.Word{
			Hangul:       wordData.Hangul,
			Romanization: wordData.Romanization,
			Type:         wordData.Type,
			CorrectCount: 0,
			WrongCount:   0,
		}

		// Create word if it doesn't exist
		result := tx.Where(models.Word{Hangul: word.Hangul}).FirstOrCreate(&word)
		if result.Error != nil {
			return fmt.Errorf("failed to create word %s: %v", word.Hangul, result.Error)
		}

		// Create translations
		for _, eng := range wordData.English {
			translation := &models.Translation{
				WordID:  word.ID,
				Hangul:  wordData.Hangul,
				English: eng,
			}
			if err := tx.Where(models.Translation{WordID: word.ID, English: eng}).FirstOrCreate(&translation).Error; err != nil {
				return fmt.Errorf("failed to create translation for word %s: %v", word.Hangul, err)
			}
		}

		// Create example sentence
		if wordData.ExampleSentence.Korean != "" && wordData.ExampleSentence.English != "" {
			sentence := &models.Sentence{
				WordID:  word.ID,
				Korean:  wordData.ExampleSentence.Korean,
				English: wordData.ExampleSentence.English,
			}
			if err := tx.Where(models.Sentence{WordID: word.ID, Korean: sentence.Korean}).FirstOrCreate(&sentence).Error; err != nil {
				return fmt.Errorf("failed to create sentence for word %s: %v", word.Hangul, err)
			}
		}
	}

	return nil
}

// loadStudyActivities creates default study activities
func loadStudyActivities(tx *gorm.DB) error {
	// Load study activities data
	dataPath := getSeedFilePath("study_activities.json")
	data, err := os.ReadFile(filepath.Clean(dataPath))
	if err != nil {
		return fmt.Errorf("could not read study_activities.json: %v", err)
	}

	var activitiesData []StudyActivitySeed
	if err := json.Unmarshal(data, &activitiesData); err != nil {
		return fmt.Errorf("failed to parse study_activities.json: %v", err)
	}

	log.Printf("Loading %d study activities from study_activities.json", len(activitiesData))

	for _, activityData := range activitiesData {
		activity := models.StudyActivity{
			Name:        activityData.Name,
			Description: activityData.Description,
			Type:        activityData.Type,
			Thumbnail:   activityData.ThumbnailURL,
			LaunchURL:   activityData.URL,
		}

		if err := tx.Where(models.StudyActivity{Name: activity.Name}).
			FirstOrCreate(&activity).Error; err != nil {
			return fmt.Errorf("failed to create activity %s: %v", activity.Name, err)
		}
	}

	return nil
}

// Add this function to seed.go

// loadGroupedWords loads word groups from word_groups.json
func loadGroupedWords(tx *gorm.DB) error {
	// Get the path to the word groups JSON file
	jsonFile := getSeedFilePath("word_groups.json")

	// Read the file
	content, err := os.ReadFile(jsonFile)
	if err != nil {
		return fmt.Errorf("could not read word_groups.json: %v", err)
	}

	// Define the structure for parsed JSON
	var jsonData struct {
		Groups map[string]struct {
			Description string `json:"description"`
			Words       []struct {
				Hangul       string      `json:"hangul"`
				Romanization string      `json:"romanization"`
				English      interface{} `json:"english"`
			} `json:"words"`
		} `json:"groups"`
	}

	// Parse the JSON
	if err := json.Unmarshal(content, &jsonData); err != nil {
		return fmt.Errorf("failed to parse word_groups.json: %v", err)
	}

	log.Printf("Loading %d word groups from word_groups.json", len(jsonData.Groups))

	// Process each group
	for groupName, groupData := range jsonData.Groups {
		// Create the word group
		wordGroup := models.WordGroup{
			Name:        groupName,
			Description: groupData.Description,
			WordsCount:  len(groupData.Words),
		}

		if err := tx.Create(&wordGroup).Error; err != nil {
			return fmt.Errorf("failed to create word group %s: %v", groupName, err)
		}

		// Process each word in this group
		for _, wordData := range groupData.Words {
			if len(wordData.Hangul) == 0 {
				continue
			}

			// Create the group word
			word := models.GROUP_Word{
				WordGroupID:  wordGroup.ID,
				Hangul:       wordData.Hangul,
				Romanization: wordData.Romanization,
			}

			if err := tx.Create(&word).Error; err != nil {
				return fmt.Errorf("failed to create word %s: %v", wordData.Hangul, err)
			}

			// Process English translations
			switch englishValue := wordData.English.(type) {
			case string:
				translation := models.GROUP_Translation{
					GROUP_WordID: word.ID,
					English:      englishValue,
				}
				if err := tx.Create(&translation).Error; err != nil {
					return fmt.Errorf("failed to create translation for word %s: %v", wordData.Hangul, err)
				}
			case []interface{}:
				for _, item := range englishValue {
					if str, ok := item.(string); ok {
						translation := models.GROUP_Translation{
							GROUP_WordID: word.ID,
							English:      str,
						}
						if err := tx.Create(&translation).Error; err != nil {
							return fmt.Errorf("failed to create translation for word %s: %v", wordData.Hangul, err)
						}
					}
				}
			}
		}

		log.Printf("Created word group '%s' with %d words", groupName, len(groupData.Words))
	}

	return nil
}

// SeedDB seeds the database with initial data
func SeedDB(db *gorm.DB) error {
	return db.Transaction(func(tx *gorm.DB) error {
		// First load all Korean words from data_korean.json
		if err := loadKoreanWords(tx); err != nil {
			return fmt.Errorf("failed to load Korean words: %v", err)
		}

		// Then load word groups from word_groups.json
		if err := loadGroupedWords(tx); err != nil {
			return fmt.Errorf("failed to load word groups: %v", err)
		}

		// Finally, create default study activities
		if err := loadStudyActivities(tx); err != nil {
			return fmt.Errorf("failed to load study activities: %v", err)
		}

		return nil
	})
}

// ResetDB drops all tables and recreates them
func ResetDB(db *gorm.DB) error {
	// Drop tables in correct order (respecting foreign key constraints)
	models := []interface{}{
		&models.Translation{},
		&models.Sentence{},
		&models.WordReviewItem{},
		&models.StudySession{},
		&models.Word{},
		&models.GROUP_Translation{},
		&models.GROUP_Word{},
		&models.WordGroup{},
		&models.StudyActivity{},
	}

	// Drop all tables
	for _, model := range models {
		if err := db.Migrator().DropTable(model); err != nil {
			return fmt.Errorf("failed to drop table for %T: %v", model, err)
		}
	}

	// Recreate tables by auto-migrating all models
	if err := db.AutoMigrate(models...); err != nil {
		return fmt.Errorf("failed to recreate tables: %v", err)
	}

	return nil
}
