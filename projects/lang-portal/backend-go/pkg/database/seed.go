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

// SeedDB seeds the database with initial data
func SeedDB(db *gorm.DB) error {
	return db.Transaction(func(tx *gorm.DB) error {
		// First load all Korean words from data_korean.json
		if err := loadKoreanWords(tx); err != nil {
			return fmt.Errorf("failed to load Korean words: %v", err)
		}

		// Then load word groups and associate words with groups
		if err := models.SeedDatabase(tx, "seed/word_groups.json"); err != nil {
			return fmt.Errorf("failed to seed word groups: %v", err)
		}

		// Finally, create default study activities
		if err := loadStudyActivities(tx); err != nil {
			return fmt.Errorf("failed to load study activities: %v", err)
		}

		return nil
	})
}
