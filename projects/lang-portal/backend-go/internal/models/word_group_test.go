package models_test

import (
	"encoding/json"
	"os"
	"testing"

	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/models"
	"github.com/stretchr/testify/assert"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

func TestWordGroupStructure(t *testing.T) {
	// Test that our WordGroup struct can properly unmarshal the JSON
	jsonData := `{
		"groups": {
			"TestGroup": {
				"description": "Test description",
				"words": [
					{
						"hangul": "테스트",
						"romanization": "teseuteu",
						"english": ["test"]
					}
				]
			}
		}
	}`

	var data models.JSONGroups
	err := json.Unmarshal([]byte(jsonData), &data)
	assert.NoError(t, err)
	assert.Len(t, data.Groups, 1)

	group, exists := data.Groups["TestGroup"]
	assert.True(t, exists)
	assert.Equal(t, "Test description", group.Description)
	assert.Len(t, group.Words, 1)
	assert.Equal(t, "테스트", group.Words[0].Hangul)
}

func TestSeedDatabase(t *testing.T) {
	// Create temp DB file
	db, err := gorm.Open(sqlite.Open("file::memory:"), &gorm.Config{})
	assert.NoError(t, err)

	// Create required tables
	err = db.AutoMigrate(&models.WordGroup{}, &models.GROUP_Word{}, &models.GROUP_Translation{})
	assert.NoError(t, err)

	// Create a small test JSON file
	testJSON := `{
		"groups": {
			"TestGroup": {
				"description": "Test description",
				"words": [
					{
						"hangul": "테스트",
						"romanization": "teseuteu",
						"english": ["test"]
					}
				]
			}
		}
	}`

	tempFile := "test_word_groups.json"
	err = os.WriteFile(tempFile, []byte(testJSON), 0644)
	assert.NoError(t, err)
	defer os.Remove(tempFile)

	// Run the seed function
	err = models.SeedDatabase(db, tempFile)
	assert.NoError(t, err)

	// Verify data was created
	var count int64
	db.Model(&models.WordGroup{}).Count(&count)
	assert.Equal(t, int64(1), count)
}
