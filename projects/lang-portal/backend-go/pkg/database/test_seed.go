package database

import (
	"encoding/json"
	"fmt"
	"log"
	"os"

	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/models"
	"gorm.io/gorm"
)

// SeedTestDB seeds the test database with test data
func SeedTestDB(db *gorm.DB) error {
	// Drop and recreate tables first
	if err := ResetDB(db); err != nil {
		return fmt.Errorf("failed to reset database: %v", err)
	}

	return db.Transaction(func(tx *gorm.DB) error {
		// Load test word groups from test_word_groups.json
		if err := loadTestGroupedWords(tx); err != nil {
			return fmt.Errorf("failed to load test word groups: %v", err)
		}

		// Load test study activities
		if err := loadTestStudyActivities(tx); err != nil {
			return fmt.Errorf("failed to load test study activities: %v", err)
		}

		return nil
	})
}

// ResetDB drops all tables and recreates them
func ResetTestDB(db *gorm.DB) error {
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

// loadTestGroupedWords loads word groups from test_word_groups.json
func loadTestGroupedWords(tx *gorm.DB) error {
	jsonFile := getSeedFilePath("test_word_groups.json")
	content, err := os.ReadFile(jsonFile)
	if err != nil {
		return fmt.Errorf("could not read test_word_groups.json: %v", err)
	}

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

	if err := json.Unmarshal(content, &jsonData); err != nil {
		return fmt.Errorf("failed to parse test_word_groups.json: %v", err)
	}

	log.Printf("Loading test word groups from test_word_groups.json")

	for groupName, groupData := range jsonData.Groups {
		wordGroup := models.WordGroup{
			Name:        groupName,
			Description: groupData.Description,
			WordsCount:  len(groupData.Words),
		}

		if err := tx.Create(&wordGroup).Error; err != nil {
			return fmt.Errorf("failed to create test word group %s: %v", groupName, err)
		}

		for _, wordData := range groupData.Words {
			if len(wordData.Hangul) == 0 {
				continue
			}

			word := models.GROUP_Word{
				WordGroupID:  wordGroup.ID,
				Hangul:       wordData.Hangul,
				Romanization: wordData.Romanization,
			}

			if err := tx.Create(&word).Error; err != nil {
				return fmt.Errorf("failed to create test word %s: %v", wordData.Hangul, err)
			}

			switch englishValue := wordData.English.(type) {
			case string:
				translation := models.GROUP_Translation{
					GROUP_WordID: word.ID,
					English:      englishValue,
				}
				if err := tx.Create(&translation).Error; err != nil {
					return fmt.Errorf("failed to create test translation: %v", err)
				}
			case []interface{}:
				for _, item := range englishValue {
					if str, ok := item.(string); ok {
						translation := models.GROUP_Translation{
							GROUP_WordID: word.ID,
							English:      str,
						}
						if err := tx.Create(&translation).Error; err != nil {
							return fmt.Errorf("failed to create test translation: %v", err)
						}
					}
				}
			}
		}

		log.Printf("Created test word group '%s' with %d words", groupName, len(groupData.Words))
	}

	return nil
}

// loadTestKoreanWords loads individual words from test_word.json
func loadTestKoreanWords(tx *gorm.DB) error {
	dataPath := getSeedFilePath("test_word.json")
	data, err := os.ReadFile(dataPath)
	if err != nil {
		return fmt.Errorf("could not read test_word.json: %v", err)
	}

	var wordsData []KoreanWordData
	if err := json.Unmarshal(data, &wordsData); err != nil {
		return fmt.Errorf("failed to parse test_word.json: %v", err)
	}

	for _, wordData := range wordsData {
		word := &models.Word{
			Hangul:       wordData.Hangul,
			Romanization: wordData.Romanization,
			Type:         wordData.Type,
			CorrectCount: 0,
			WrongCount:   0,
		}

		result := tx.Where(models.Word{Hangul: word.Hangul}).FirstOrCreate(&word)
		if result.Error != nil {
			return fmt.Errorf("failed to create test word %s: %v", word.Hangul, result.Error)
		}

		for _, eng := range wordData.English {
			translation := &models.Translation{
				WordID:  word.ID,
				Hangul:  wordData.Hangul,
				English: eng,
			}
			if err := tx.Where(models.Translation{WordID: word.ID, English: eng}).FirstOrCreate(&translation).Error; err != nil {
				return fmt.Errorf("failed to create test translation: %v", err)
			}
		}

		if wordData.ExampleSentence.Korean != "" && wordData.ExampleSentence.English != "" {
			sentence := &models.Sentence{
				WordID:  word.ID,
				Korean:  wordData.ExampleSentence.Korean,
				English: wordData.ExampleSentence.English,
			}
			if err := tx.Where(models.Sentence{WordID: word.ID, Korean: sentence.Korean}).FirstOrCreate(&sentence).Error; err != nil {
				return fmt.Errorf("failed to create test sentence: %v", err)
			}
		}
	}

	return nil
}

func loadTestStudyActivities(tx *gorm.DB) error {
	jsonFile := getSeedFilePath("test_study_activities.json")
	data, err := os.ReadFile(jsonFile)
	if err != nil {
		return fmt.Errorf("could not read test_study_activities.json: %v", err)
	}

	var activitiesData struct {
		Activities []struct {
			Name        string `json:"name"`
			Description string `json:"description"`
			Type        string `json:"type"`
			Thumbnail   string `json:"thumbnail_url"`
			LaunchURL   string `json:"url"`
		} `json:"activities"`
	}

	if err := json.Unmarshal(data, &activitiesData); err != nil {
		return fmt.Errorf("failed to parse test_study_activities.json: %v", err)
	}

	log.Printf("Loading %d test study activities", len(activitiesData.Activities))

	for _, activityData := range activitiesData.Activities {
		activity := models.StudyActivity{
			Name:        activityData.Name,
			Description: activityData.Description,
			Type:        activityData.Type,
			Thumbnail:   activityData.Thumbnail,
			LaunchURL:   activityData.LaunchURL,
		}

		if err := tx.Create(&activity).Error; err != nil {
			return fmt.Errorf("failed to create test activity %s: %v", activity.Name, err)
		}
		log.Printf("✅ Created test activity: %s", activity.Name)
	}

	return nil
}
