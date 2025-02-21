package models_test

import (
	"testing"
	"time"

	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/models"
	"github.com/stretchr/testify/assert"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

// TestWordModel tests the basic functionality of the Word model
func TestWordModel(t *testing.T) {
	// Create a new word
	word := models.Word{
		Hangul:       "테스트",
		Romanization: "teseuteu",
		Type:         "noun",
		CorrectCount: 0,
		WrongCount:   0,
	}

	// Check values
	assert.Equal(t, "테스트", word.Hangul)
	assert.Equal(t, "teseuteu", word.Romanization)
	assert.Equal(t, "noun", word.Type)
	assert.Equal(t, 0, word.CorrectCount)
	assert.Equal(t, 0, word.WrongCount)
}

// TestWordWithTranslation tests that translations are correctly associated with words
func TestWordWithTranslation(t *testing.T) {
	// Setup in-memory database
	db, err := gorm.Open(sqlite.Open("file::memory:"), &gorm.Config{})
	assert.NoError(t, err)

	// Migrate tables
	err = db.AutoMigrate(&models.Word{}, &models.Translation{})
	assert.NoError(t, err)

	// Create a word with translations
	word := models.Word{
		Hangul:       "테스트",
		Romanization: "teseuteu",
		Type:         "noun",
	}

	err = db.Create(&word).Error
	assert.NoError(t, err)
	assert.NotZero(t, word.ID)

	// Create translations
	translations := []models.Translation{
		{
			WordID:  word.ID,
			English: "test",
		},
		{
			WordID:  word.ID,
			English: "experiment",
		},
	}

	for _, translation := range translations {
		err = db.Create(&translation).Error
		assert.NoError(t, err)
	}

	// Retrieve the word with translations
	var retrievedWord models.Word
	err = db.Preload("EnglishTranslations").First(&retrievedWord, word.ID).Error
	assert.NoError(t, err)

	// Check the translations were loaded
	assert.Len(t, retrievedWord.EnglishTranslations, 2)
	assert.Equal(t, "test", retrievedWord.EnglishTranslations[0].English)
	assert.Equal(t, "experiment", retrievedWord.EnglishTranslations[1].English)
}

// TestWordWithSentences tests that sentences are correctly associated with words
func TestWordWithSentences(t *testing.T) {
	// Setup in-memory database
	db, err := gorm.Open(sqlite.Open("file::memory:"), &gorm.Config{})
	assert.NoError(t, err)

	// Migrate tables
	err = db.AutoMigrate(&models.Word{}, &models.Sentence{})
	assert.NoError(t, err)

	// Create a word with sentences
	word := models.Word{
		Hangul:       "테스트",
		Romanization: "teseuteu",
		Type:         "noun",
	}

	err = db.Create(&word).Error
	assert.NoError(t, err)

	// Create sentences
	sentences := []models.Sentence{
		{
			WordID:  word.ID,
			Korean:  "이것은 테스트입니다.",
			English: "This is a test.",
		},
		{
			WordID:  word.ID,
			Korean:  "테스트를 하고 있어요.",
			English: "I am testing.",
		},
	}

	for _, sentence := range sentences {
		err = db.Create(&sentence).Error
		assert.NoError(t, err)
	}

	// Retrieve the word with sentences
	var retrievedWord models.Word
	err = db.Preload("Sentences").First(&retrievedWord, word.ID).Error
	assert.NoError(t, err)

	// Check the sentences were loaded
	assert.Len(t, retrievedWord.Sentences, 2)
	assert.Equal(t, "이것은 테스트입니다.", retrievedWord.Sentences[0].Korean)
	assert.Equal(t, "This is a test.", retrievedWord.Sentences[0].English)
	assert.Equal(t, "테스트를 하고 있어요.", retrievedWord.Sentences[1].Korean)
	assert.Equal(t, "I am testing.", retrievedWord.Sentences[1].English)
}

// TestAfterFind tests that the AfterFind hook correctly converts translations to the English field
func TestAfterFind(t *testing.T) {
	// Setup in-memory database
	db, err := gorm.Open(sqlite.Open("file::memory:"), &gorm.Config{})
	assert.NoError(t, err)

	// Migrate tables
	err = db.AutoMigrate(&models.Word{}, &models.Translation{})
	assert.NoError(t, err)

	// Create a word with translations
	word := models.Word{
		Hangul:       "테스트",
		Romanization: "teseuteu",
		Type:         "noun",
	}

	err = db.Create(&word).Error
	assert.NoError(t, err)

	// Create translations
	translations := []models.Translation{
		{
			WordID:  word.ID,
			English: "test",
		},
		{
			WordID:  word.ID,
			English: "experiment",
		},
	}

	for _, translation := range translations {
		err = db.Create(&translation).Error
		assert.NoError(t, err)
	}

	// Retrieve the word with translations
	var retrievedWord models.Word
	err = db.Preload("EnglishTranslations").First(&retrievedWord, word.ID).Error
	assert.NoError(t, err)

	// Check the English field was populated by the AfterFind hook
	assert.NotNil(t, retrievedWord.English)
	assert.Len(t, retrievedWord.English, 2)
	assert.Contains(t, retrievedWord.English, "test")
	assert.Contains(t, retrievedWord.English, "experiment")
}

// TestWordStatistics tests that correct and wrong counts are properly updated
func TestWordStatistics(t *testing.T) {
	// Setup in-memory database
	db, err := gorm.Open(sqlite.Open("file::memory:"), &gorm.Config{})
	assert.NoError(t, err)

	// Migrate tables
	err = db.AutoMigrate(&models.Word{})
	assert.NoError(t, err)

	// Create a word
	word := models.Word{
		Hangul:       "테스트",
		Romanization: "teseuteu",
		Type:         "noun",
		CorrectCount: 0,
		WrongCount:   0,
	}

	err = db.Create(&word).Error
	assert.NoError(t, err)

	// Increment correct count
	err = db.Model(&word).Update("correct_count", gorm.Expr("correct_count + ?", 1)).Error
	assert.NoError(t, err)

	// Increment wrong count
	err = db.Model(&word).Update("wrong_count", gorm.Expr("wrong_count + ?", 1)).Error
	assert.NoError(t, err)

	// Retrieve the updated word
	var retrievedWord models.Word
	err = db.First(&retrievedWord, word.ID).Error
	assert.NoError(t, err)

	// Check the counts were updated
	assert.Equal(t, 1, retrievedWord.CorrectCount)
	assert.Equal(t, 1, retrievedWord.WrongCount)
}

// TestWordCreatedUpdatedAt tests that created_at and updated_at fields are set
// TestWordCreatedUpdatedAt tests that created_at and updated_at fields are set
func TestWordCreatedUpdatedAt(t *testing.T) {
	// Setup in-memory database
	db, err := gorm.Open(sqlite.Open("file::memory:"), &gorm.Config{})
	assert.NoError(t, err)

	// Migrate tables
	err = db.AutoMigrate(&models.Word{})
	assert.NoError(t, err)

	// Create a word
	word := models.Word{
		Hangul:       "테스트",
		Romanization: "teseuteu",
		Type:         "noun",
	}

	// Get current time for comparison
	beforeCreate := time.Now().Add(-time.Second)

	err = db.Create(&word).Error
	assert.NoError(t, err)

	// Check timestamps
	assert.NotZero(t, word.CreatedAt)
	assert.NotZero(t, word.UpdatedAt)

	// Compare times by converting to Unix timestamp (ignoring time zone)
	assert.True(t, word.CreatedAt.Unix() >= beforeCreate.Unix())
	assert.True(t, word.UpdatedAt.Unix() >= beforeCreate.Unix())

	// Update the word
	time.Sleep(time.Millisecond * 10) // Ensure time difference
	beforeUpdate := time.Now()

	err = db.Model(&word).Update("romanization", "teseuteu-update").Error
	assert.NoError(t, err)

	// Retrieve the updated word
	var retrievedWord models.Word
	err = db.First(&retrievedWord, word.ID).Error
	assert.NoError(t, err)

	// Check updated_at was updated but created_at was not
	// Compare the dates only, not the timestamps including timezone
	assert.Equal(t, word.CreatedAt.Format(time.RFC3339), retrievedWord.CreatedAt.Format(time.RFC3339))
	assert.True(t, retrievedWord.UpdatedAt.Unix() >= beforeUpdate.Unix())
}
