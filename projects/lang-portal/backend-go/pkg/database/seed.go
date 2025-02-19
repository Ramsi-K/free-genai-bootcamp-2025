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

// WordGroupData represents the structure of word_groups.json
type WordGroupData struct {
	Groups map[string]struct {
		Description string `json:"description"`
		Words       []struct {
			Hangul          string   `json:"hangul"`
			Romanization    string   `json:"romanization"`
			Type            string   `json:"type"`
			English         []string `json:"english"`
			ExampleSentence struct {
				Korean  string `json:"korean"`
				English string `json:"english"`
			} `json:"example_sentence"`
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

// loadWordGroups loads word groups and associates words with groups
func loadWordGroups(tx *gorm.DB) error {
	// Load word groups data
	dataPath := getSeedFilePath("word_groups.json")
	data, err := os.ReadFile(filepath.Clean(dataPath))
	if err != nil {
		return fmt.Errorf("could not read word_groups.json: %v", err)
	}

	var wordGroupsData WordGroupData
	if err := json.Unmarshal(data, &wordGroupsData); err != nil {
		return fmt.Errorf("failed to parse word_groups.json: %v", err)
	}

	log.Printf("Loading word groups from word_groups.json")

	// Create word groups and associate words
	for groupName, groupData := range wordGroupsData.Groups {
		group := &models.WordGroup{
			Name:        groupName,
			Description: groupData.Description,
		}

		// Create group if it doesn't exist
		result := tx.Where(models.WordGroup{Name: group.Name}).FirstOrCreate(&group)
		if result.Error != nil {
			return fmt.Errorf("failed to create group %s: %v", group.Name, result.Error)
		}

		// Associate existing words with group
		for _, wordData := range groupData.Words {
			var word models.Word
			// Find the word by Hangul
			if err := tx.Where("hangul = ?", wordData.Hangul).First(&word).Error; err != nil {
				log.Printf("Warning: Word %s not found for group %s", wordData.Hangul, groupName)
				continue
			}

			// Associate word with group if not already associated
			if err := tx.Model(group).Association("Words").Append(&word); err != nil {
				return fmt.Errorf("failed to associate word %s with group %s: %v", word.Hangul, group.Name, err)
			}
		}

		// Update WordsCount
		var count int64
		if err := tx.Model(&models.Word{}).
			Joins("JOIN group_words ON group_words.word_id = words.id").
			Where("group_words.word_group_id = ?", group.ID).
			Count(&count).Error; err != nil {
			return fmt.Errorf("failed to count words for group %s: %v", group.Name, err)
		}

		group.WordsCount = int(count)
		if err := tx.Save(group).Error; err != nil {
			return fmt.Errorf("failed to update word count for group %s: %v", group.Name, err)
		}
	}

	return nil
}

// loadStudyActivities creates default study activities
func loadStudyActivities(tx *gorm.DB) error {
	activities := []models.StudyActivity{
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

	for _, activity := range activities {
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
		if err := loadWordGroups(tx); err != nil {
			return fmt.Errorf("failed to load word groups: %v", err)
		}

		// Finally, create default study activities
		if err := loadStudyActivities(tx); err != nil {
			return fmt.Errorf("failed to load study activities: %v", err)
		}

		return nil
	})
}
