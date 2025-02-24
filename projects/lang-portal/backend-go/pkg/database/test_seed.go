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

// SeedTestDB seeds the test database with test data
func SeedTestDB(db *gorm.DB) error {
	if err := ResetTestDB(db); err != nil {
		return fmt.Errorf("failed to reset database: %v", err)
	}

	return db.Transaction(func(tx *gorm.DB) error {
		// Load individual words first (for word-based tests)
		if err := loadTestKoreanWords(tx); err != nil {
			return fmt.Errorf("failed to load test word: %v", err)
		}

		// Load word groups (completely separate from words)
		if err := loadTestGroupedWords(tx); err != nil {
			return fmt.Errorf("failed to load test word groups: %v", err)
		}

		// Load activities
		if err := loadTestStudyActivities(tx); err != nil {
			return fmt.Errorf("failed to load test study activities: %v", err)
		}

		// Load study sessions
		if err := loadTestStudySessions(tx); err != nil {
			return fmt.Errorf("failed to load test study sessions: %v", err)
		}

		// Load study progress
		if err := loadTestStudyProgress(tx); err != nil {
			return fmt.Errorf("failed to load test study progress: %v", err)
		}

		// Load quick stats
		if err := loadTestQuickStats(tx); err != nil {
			return fmt.Errorf("failed to load test quick stats: %v", err)
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
		&models.StudyProgress{}, // Add this
		&models.QuickStats{},    // Add this
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
		// Create WordGroup
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

			// ONLY create GROUP_Word - NO Word creation
			groupWord := models.GROUP_Word{
				WordGroupID:  wordGroup.ID,
				Hangul:       wordData.Hangul,
				Romanization: wordData.Romanization,
			}

			if err := tx.Create(&groupWord).Error; err != nil {
				return fmt.Errorf("failed to create test group word %s: %v", wordData.Hangul, err)
			}

			// Handle GROUP_Translation
			switch englishValue := wordData.English.(type) {
			case string:
				groupTranslation := models.GROUP_Translation{
					GROUP_WordID: groupWord.ID,
					English:      englishValue,
				}
				if err := tx.Create(&groupTranslation).Error; err != nil {
					return fmt.Errorf("failed to create test group translation: %v", err)
				}
			case []interface{}:
				for _, item := range englishValue {
					if str, ok := item.(string); ok {
						groupTranslation := models.GROUP_Translation{
							GROUP_WordID: groupWord.ID,
							English:      str,
						}
						if err := tx.Create(&groupTranslation).Error; err != nil {
							return fmt.Errorf("failed to create test group translation: %v", err)
						}
					}
				}
			}
		}
	}

	return nil
}

// loadTestKoreanWords loads individual words from test_word.json
func loadTestKoreanWords(tx *gorm.DB) error {
	// Use getSeedFilePath helper instead of direct path
	jsonFile := getSeedFilePath("test_word.json")
	content, err := os.ReadFile(jsonFile)
	if err != nil {
		return fmt.Errorf("failed to read test_word.json: %v", err)
	}

	var testWords []struct {
		Hangul          string   `json:"hangul"`
		Romanization    string   `json:"romanization"`
		Type            string   `json:"type"`
		English         []string `json:"english"`
		ExampleSentence struct {
			Korean  string `json:"korean"`
			English string `json:"english"`
		} `json:"example_sentence"`
	}

	if err := json.Unmarshal(content, &testWords); err != nil {
		return fmt.Errorf("failed to parse test_word.json: %v", err)
	}

	// Create words with their sentences
	for _, tw := range testWords {
		word := models.Word{
			Hangul:       tw.Hangul,
			Romanization: tw.Romanization,
			Type:         tw.Type,
		}

		if err := tx.Create(&word).Error; err != nil {
			return fmt.Errorf("failed to create test word: %v", err)
		}

		// Create translations
		for _, eng := range tw.English {
			translation := models.Translation{
				WordID:  word.ID,
				English: eng,
			}
			if err := tx.Create(&translation).Error; err != nil {
				return fmt.Errorf("failed to create translation: %v", err)
			}
		}

		// Create sentence if it exists
		if tw.ExampleSentence.Korean != "" {
			sentence := models.Sentence{
				WordID:  word.ID,
				Korean:  tw.ExampleSentence.Korean,
				English: tw.ExampleSentence.English,
			}
			if err := tx.Create(&sentence).Error; err != nil {
				return fmt.Errorf("failed to create test sentence: %v", err)
			}
			log.Printf("✅ Created test sentence for word %s: %s", word.Hangul, sentence.Korean)
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

func loadTestStudySessions(tx *gorm.DB) error {
	jsonFile := getSeedFilePath("test_study_sessions.json")
	data, err := os.ReadFile(jsonFile)
	if err != nil {
		return fmt.Errorf("could not read test_study_sessions.json: %v", err)
	}

	var sessionsData struct {
		StudySessions []models.StudySession `json:"study_sessions"`
	}

	if err := json.Unmarshal(data, &sessionsData); err != nil {
		return fmt.Errorf("failed to parse test_study_sessions.json: %v", err)
	}

	for _, session := range sessionsData.StudySessions {
		if err := tx.Create(&session).Error; err != nil {
			return fmt.Errorf("failed to create test study session: %v", err)
		}
	}

	return nil
}

func loadTestStudyProgress(tx *gorm.DB) error {
	jsonFile := getSeedFilePath("test_study_progress.json")
	data, err := os.ReadFile(jsonFile)
	if err != nil {
		return fmt.Errorf("could not read test_study_progress.json: %v", err)
	}

	var progressData struct {
		StudyProgress []models.StudyProgress `json:"study_progress"`
	}

	if err := json.Unmarshal(data, &progressData); err != nil {
		return fmt.Errorf("failed to parse test_study_progress.json: %v", err)
	}

	for _, progress := range progressData.StudyProgress {
		if err := tx.Create(&progress).Error; err != nil {
			return fmt.Errorf("failed to create test study progress: %v", err)
		}
	}

	return nil
}

func loadTestQuickStats(tx *gorm.DB) error {
	jsonFile := getSeedFilePath("test_quick_stats.json")
	data, err := os.ReadFile(jsonFile)
	if err != nil {
		return fmt.Errorf("could not read test_quick_stats.json: %v", err)
	}

	var statsData struct {
		QuickStats []models.QuickStats `json:"quick_stats"`
	}

	if err := json.Unmarshal(data, &statsData); err != nil {
		return fmt.Errorf("failed to parse test_quick_stats.json: %v", err)
	}

	for _, stats := range statsData.QuickStats {
		if err := tx.Create(&stats).Error; err != nil {
			return fmt.Errorf("failed to create test quick stats: %v", err)
		}
	}

	return nil
}

func loadTestData(filename string, v interface{}) error {
	jsonFile := filepath.Join("seed", filename)
	data, err := os.ReadFile(jsonFile)
	if err != nil {
		return fmt.Errorf("could not read %s: %v", filename, err)
	}

	// Unmarshal JSON data into the provided interface
	if err := json.Unmarshal(data, v); err != nil {
		return fmt.Errorf("failed to parse %s: %v", filename, err)
	}

	return nil
}
