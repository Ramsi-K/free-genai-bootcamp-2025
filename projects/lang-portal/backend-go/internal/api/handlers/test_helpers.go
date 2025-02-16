package handlers

import (
	"encoding/json"
	"fmt"
	"net/http/httptest"
	"testing"

	"github.com/Ramsi-K/free-genai-bootcamp-2025/tree/main/projects/lang-portal/backend-go/internal/models"

	"github.com/gin-gonic/gin"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

// setupTestRouter creates a test router with the given handlers
func setupTestRouter(h interface{}) *gin.Engine {
	gin.SetMode(gin.TestMode)
	r := gin.New()

	api := r.Group("/api")

	switch handler := h.(type) {
	case *WordHandler:
		api.GET("/words", handler.List)
		api.GET("/words/:id", handler.Get)
	case *StudySessionHandler:
		api.POST("/study_sessions", handler.Create)
	}

	return r
}

// createMockDB returns a mock DB with test data
func createMockDB(t *testing.T) *gorm.DB {
	// Create mock words without explicit IDs
	mockWords := []models.Word{
		{
			Hangul:         "학교",
			Romanization:   "hakgyo",
			English:        []string{"school"},
			Type:           "noun",
			ExampleKorean:  "나는 학교에 갑니다",
			ExampleEnglish: "I go to school",
		},
		{
			Hangul:         "사과",
			Romanization:   "sagwa",
			English:        []string{"apple"},
			Type:           "noun",
			ExampleKorean:  "사과를 먹습니다",
			ExampleEnglish: "I eat an apple",
		},
	}

	// Create a unique in-memory database for each test
	db, err := gorm.Open(sqlite.Open("file::memory:?cache=shared"), &gorm.Config{
		// Disable logger for tests
		Logger: nil,
	})
	if err != nil {
		t.Fatalf("Failed to create test database: %v", err)
	}

	// Migrate schema
	if err := db.AutoMigrate(
		&models.Word{},
		&models.Group{},
		&models.StudySession{},
		&models.StudyActivity{},
		&models.WordReview{},
		&models.WordsGroups{},
	); err != nil {
		t.Fatalf("Failed to migrate test database: %v", err)
	}

	// Insert test data
	if err := db.Create(&mockWords).Error; err != nil {
		t.Fatalf("Failed to insert test data: %v", err)
	}

	// Create test group without explicit ID
	group := models.Group{
		Name: "Test Group",
	}
	if err := db.Create(&group).Error; err != nil {
		t.Fatalf("Failed to create test group: %v", err)
	}

	// Store the first word's ID for tests that need it
	var firstWord models.Word
	if err := db.First(&firstWord).Error; err != nil {
		t.Fatalf("Failed to get first word: %v", err)
	}
	t.Setenv("TEST_WORD_ID", fmt.Sprintf("%d", firstWord.ID))

	return db
}

// parseResponse parses JSON response into map
func parseResponse(w *httptest.ResponseRecorder) (map[string]interface{}, error) {
	var response map[string]interface{}
	err := json.Unmarshal(w.Body.Bytes(), &response)
	return response, err
}

// parseWordList parses JSON response into word list
func parseWordList(w *httptest.ResponseRecorder) ([]map[string]interface{}, error) {
	var response []map[string]interface{}
	err := json.Unmarshal(w.Body.Bytes(), &response)
	return response, err
}

// setupTestDB creates a test database with the given test data
func setupTestDB(t *testing.T, words []models.Word) *gorm.DB {
	// Create a unique in-memory database for each test
	db, err := gorm.Open(sqlite.Open("file::memory:"), &gorm.Config{
		Logger: nil, // Disable logger for tests
	})
	if err != nil {
		t.Fatalf("Failed to create test database: %v", err)
	}

	// Migrate schema
	if err := db.AutoMigrate(
		&models.Word{},
		&models.Group{},
		&models.StudySession{},
		&models.WordReview{},
		&models.WordsGroups{},
	); err != nil {
		t.Fatalf("Failed to migrate test database: %v", err)
	}

	// Insert test data
	if err := db.Create(&words).Error; err != nil {
		t.Fatalf("Failed to insert test data: %v", err)
	}

	return db
}
