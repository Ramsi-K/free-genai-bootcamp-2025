package database

import (
	"encoding/json"
	"log"
	"os"
	"path/filepath"

	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/models"
	"gorm.io/gorm"
)

// WordGroupData represents the structure of word_groups.json
type WordGroupData struct {
	Groups map[string]struct {
		Description string `json:"description"`
		Words       []struct {
			Hangul       string   `json:"hangul"`
			Romanization string   `json:"romanization"`
			English      []string `json:"english"`
		} `json:"words"`
	} `json:"groups"`
}

// StudyActivitySeed represents the structure of study_activities.json
type StudyActivitySeed struct {
	Name         string `json:"name"`
	Description  string `json:"description"`
	Type         string `json:"type"`
	ThumbnailURL string `json:"thumbnail_url"`
	URL          string `json:"url"`
}

// LoadSeedData loads initial data from JSON files
func LoadSeedData(db *gorm.DB) error {
	// Use transaction to ensure data consistency
	return db.Transaction(func(tx *gorm.DB) error {
		// Load word groups data
		data, err := os.ReadFile(filepath.Clean("seed/word_groups.json"))
		if err != nil {
			return err
		}

		var wordGroupData WordGroupData
		if err := json.Unmarshal(data, &wordGroupData); err != nil {
			return err
		}

		// Create word groups and their associated words
		for groupName, groupData := range wordGroupData.Groups {
			// Create word group
			group := &models.WordGroup{
				Name:        groupName,
				Description: groupData.Description,
				WordsCount:  len(groupData.Words), // Set initial word count
			}

			// Only create if it doesn't exist
			if err := tx.Where(models.WordGroup{Name: groupName}).
				FirstOrCreate(group).Error; err != nil {
				return err
			}

			// Create words for this group
			for _, wordData := range groupData.Words {
				word := models.Word{
					Hangul:       wordData.Hangul,
					Romanization: wordData.Romanization,
					English:      models.StringSlice(wordData.English),
					Type:         "noun", // Default type
					ExampleSentence: models.ExampleSentence{
						Korean:  "", // These can be populated later
						English: "",
					},
					StudyStatistics: models.StudyStatistics{
						CorrectCount: 0,
						WrongCount:   0,
					},
				}

				// Create word if it doesn't exist
				if err := tx.Where(models.Word{Hangul: word.Hangul}).
					FirstOrCreate(&word).Error; err != nil {
					return err
				}

				// Associate word with group
				if err := tx.Model(&word).Association("Groups").Append(group); err != nil {
					return err
				}
			}

			// Update word count after creating all associations
			var count int64
			if err := tx.Model(&models.Word{}).
				Joins("JOIN group_words ON group_words.word_id = words.id").
				Where("group_words.word_group_id = ?", group.ID).
				Count(&count).Error; err != nil {
				return err
			}

			// Update the group's word count
			if err := tx.Model(group).Update("words_count", count).Error; err != nil {
				return err
			}
		}

		// Create default study activities
		defaultActivities := []models.StudyActivity{
			{
				Name:        "Flashcards",
				Description: "Practice words with flashcards",
				Type:        "flashcards",
				Thumbnail:   "/images/flashcards.png",
				LaunchURL:   "/study/flashcards",
			},
			{
				Name:        "Multiple Choice",
				Description: "Test your knowledge with multiple choice questions",
				Type:        "quiz",
				Thumbnail:   "/images/quiz.png",
				LaunchURL:   "/study/quiz",
			},
			{
				Name:        "Typing Practice",
				Description: "Practice typing Korean words",
				Type:        "typing",
				Thumbnail:   "/images/typing.png",
				LaunchURL:   "/study/typing",
			},
		}

		// Create activities
		for _, activity := range defaultActivities {
			if err := tx.Where(models.StudyActivity{Name: activity.Name}).
				FirstOrCreate(&activity).Error; err != nil {
				return err
			}
		}

		log.Println("Seed data loaded successfully")
		return nil
	})
}
