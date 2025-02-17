package handlers

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"os"
	"testing"
	"time"

	"github.com/Ramsi-K/free-genai-bootcamp-2025/tree/main/projects/lang-portal/backend-go/internal/models"

	"github.com/gin-gonic/gin"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

type testHelper struct {
	db     *gorm.DB
	router *gin.Engine
}

func newTestHelper(t *testing.T) (*testHelper, error) {
	// Create a temporary database file
	tmpfile, err := os.CreateTemp("", "test-*.db")
	if err != nil {
		return nil, err
	}

	// Open database connection
	db, err := gorm.Open(sqlite.Open(tmpfile.Name()), &gorm.Config{})
	if err != nil {
		return nil, err
	}

	// Auto migrate tables
	err = db.AutoMigrate(
		&models.Word{},
		&models.Group{},
		&models.WordsGroups{},
		&models.StudyActivity{},
		&models.StudySession{},
		&models.WordReview{},
	)
	if err != nil {
		return nil, err
	}

	// Setup router
	gin.SetMode(gin.TestMode)
	router := gin.New()
	router.Use(gin.Recovery())

	return &testHelper{
		db:     db,
		router: router,
	}, nil
}

func (h *testHelper) seedTestData() error {
	// Create test words
	words := []models.Word{
		{
			Hangul:       "학교",
			Romanization: "hakgyo",
			English:      []string{"school"},
			Type:         "noun",
			Example: models.Example{
				Korean:  "그는 학교에서 저보다 한 학년 위였어요.",
				English: "He was a year ahead of me in school.",
			},
		},
		{
			Hangul:       "학생",
			Romanization: "haksaeng",
			English:      []string{"student"},
			Type:         "noun",
			Example: models.Example{
				Korean:  "그는 좋은 학생이에요.",
				English: "He is a good student.",
			},
		},
	}

	for _, word := range words {
		if err := h.db.Create(&word).Error; err != nil {
			return err
		}
	}

	// Create test groups
	groups := []models.Group{
		{
			Name:       "School-related Words",
			WordsCount: 2,
		},
		{
			Name:       "Basic Words",
			WordsCount: 0,
		},
	}

	for _, group := range groups {
		if err := h.db.Create(&group).Error; err != nil {
			return err
		}
	}

	// Create test study activities
	activities := []models.StudyActivity{
		{
			Name:         "Flashcards",
			Description:  "Practice words with flashcards",
			Type:         "flashcards",
			ThumbnailURL: "/images/flashcards.png",
		},
		{
			Name:         "Multiple Choice",
			Description:  "Practice with multiple choice questions",
			Type:         "multiple_choice",
			ThumbnailURL: "/images/multiple-choice.png",
		},
	}

	for _, activity := range activities {
		if err := h.db.Create(&activity).Error; err != nil {
			return err
		}
	}

	// Create test study session
	now := time.Now()
	session := models.StudySession{
		GroupID:         1,
		StudyActivityID: 1,
		CompletedAt:     &now,
	}

	if err := h.db.Create(&session).Error; err != nil {
		return err
	}

	// Create test word reviews
	reviews := []models.WordReview{
		{
			WordID:         1,
			StudySessionID: 1,
			Correct:        true,
		},
		{
			WordID:         2,
			StudySessionID: 1,
			Correct:        false,
		},
	}

	for _, review := range reviews {
		if err := h.db.Create(&review).Error; err != nil {
			return err
		}
	}

	// Link words to groups
	if err := h.db.Exec("INSERT INTO words_groups (word_id, group_id) VALUES (1, 1), (2, 1)").Error; err != nil {
		return err
	}

	return nil
}

func performRequest(r http.Handler, method, path string, body interface{}) *httptest.ResponseRecorder {
	var reqBody []byte
	if body != nil {
		reqBody, _ = json.Marshal(body)
	}
	req := httptest.NewRequest(method, path, bytes.NewBuffer(reqBody))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)
	return w
}

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

func setupTestRouter(db *gorm.DB) *gin.Engine {
	gin.SetMode(gin.TestMode)
	r := gin.New()
	r.Use(gin.Recovery())
	return r
}
