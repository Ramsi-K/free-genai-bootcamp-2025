package handlers

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/models"
	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/repository"
	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
	"gorm.io/gorm"
)

func TestWordHandler_Integration(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test")
	}

	// Setup
	db, err := setupTestDB()
	if err != nil {
		t.Fatalf("Failed to setup test database: %v", err)
	}
	defer cleanupTestDB(db)

	// Create test data
	_, err = createTestWord(db, "테스트1")
	if err != nil {
		t.Fatalf("Failed to create test word: %v", err)
	}

	_, err = createTestWord(db, "테스트2")
	if err != nil {
		t.Fatalf("Failed to create test word: %v", err)
	}

	// Setup router
	gin.SetMode(gin.TestMode)
	router := gin.New()
	repo := repository.NewWordRepository(repository.NewBaseRepository(db))
	handler := NewWordHandler(repo)

	router.GET("/api/words", handler.ListWords)
	router.GET("/api/words/:id", handler.GetWord)
	router.POST("/api/words/:id/correct", handler.CreateCorrectStudySession)
	router.POST("/api/words/:id/incorrect", handler.CreateIncorrectStudySession)

	// Test cases
	tests := []struct {
		name           string
		path           string
		method         string
		expectedStatus int
		validateBody   func(t *testing.T, body []byte)
		setup          func(db *gorm.DB)
	}{
		{
			name:           "List Words",
			path:           "/api/words",
			method:         "GET",
			expectedStatus: http.StatusOK,
			validateBody: func(t *testing.T, body []byte) {
				var response struct {
					Data []models.Word `json:"data"`
					Meta struct {
						CurrentPage int   `json:"current_page"`
						PerPage     int   `json:"per_page"`
						Total       int64 `json:"total"`
					} `json:"meta"`
				}
				assert.NoError(t, json.Unmarshal(body, &response))
				assert.Len(t, response.Data, 2)
				assert.Equal(t, 1, response.Meta.CurrentPage)
				assert.Equal(t, 10, response.Meta.PerPage)
				assert.Equal(t, int64(2), response.Meta.Total)

				// Validate word fields
				for _, word := range response.Data {
					assert.NotEmpty(t, word.ID)
					assert.NotEmpty(t, word.Hangul)
					assert.NotEmpty(t, word.Romanization)
					assert.NotEmpty(t, word.Type)
					assert.NotEmpty(t, word.EnglishTranslations)
					assert.NotEmpty(t, word.Sentences[0].Korean)
					assert.NotEmpty(t, word.Sentences[0].English)
					assert.NotZero(t, word.CreatedAt)
					assert.NotZero(t, word.UpdatedAt)
				}
			},
		},
		{
			name:           "List Words - Invalid Page",
			path:           "/api/words?page=invalid",
			method:         "GET",
			expectedStatus: http.StatusBadRequest,
		},
		{
			name:           "List Words - Invalid Limit",
			path:           "/api/words?limit=0",
			method:         "GET",
			expectedStatus: http.StatusBadRequest,
		},
		{
			name:           "List Words - Negative Page",
			path:           "/api/words?page=-1",
			method:         "GET",
			expectedStatus: http.StatusBadRequest,
		},
		{
			name:           "Get Word",
			path:           "/api/words/1",
			method:         "GET",
			expectedStatus: http.StatusOK,
			validateBody: func(t *testing.T, body []byte) {
				var word models.Word
				assert.NoError(t, json.Unmarshal(body, &word))
				assert.Equal(t, uint(1), word.ID)
				assert.Equal(t, "테스트1", word.Hangul)
				assert.Equal(t, "test", word.Romanization)
				assert.Equal(t, "noun", word.Type)
				assert.Equal(t, []string{"test"}, word.EnglishTranslations)
				assert.Equal(t, "Test Korean sentence", word.Sentences[0].Korean)
				assert.Equal(t, "Test English sentence", word.Sentences[0].English)
				assert.NotZero(t, word.CreatedAt)
				assert.NotZero(t, word.UpdatedAt)
			},
		},
		{
			name:           "Get Non-existent Word",
			path:           "/api/words/999",
			method:         "GET",
			expectedStatus: http.StatusNotFound,
		},
		{
			name:           "Get Word with Invalid ID",
			path:           "/api/words/invalid",
			method:         "GET",
			expectedStatus: http.StatusBadRequest,
		},
		{
			name:           "Create Correct Study Session",
			path:           "/api/words/1/correct",
			method:         "POST",
			expectedStatus: http.StatusCreated,
			setup: func(db *gorm.DB) {
				// Reset database before each test
				if err := resetTestDB(db); err != nil {
					t.Fatalf("Failed to reset test database: %v", err)
				}

				// Create test data again after reset
				_, err = createTestWord(db, "테스트1")
				if err != nil {
					t.Fatalf("Failed to create test word: %v", err)
				}
			},
			validateBody: func(t *testing.T, body []byte) {
				var response map[string]interface{}
				assert.NoError(t, json.Unmarshal(body, &response))
				assert.Equal(t, "Study session created", response["message"])

				// Verify that a new StudySession record was created
				var studySessions []models.StudySession
				if err := db.Find(&studySessions).Error; err != nil {
					t.Fatalf("Failed to find study sessions: %v", err)
				}

				assert.Len(t, studySessions, 1)

				// Retrieve the associated WordReviewItem
				var wordReviewItem models.WordReviewItem
				if err := db.Where("study_session_id = ?", studySessions[0].ID).First(&wordReviewItem).Error; err != nil {
					t.Fatalf("Failed to find word review item: %v", err)
				}

				// Assert that the WordID and Correct values match the expected values
				assert.Equal(t, uint(1), wordReviewItem.WordID)
				// Correct is an integer (0 or 1)
				assert.Equal(t, 1, wordReviewItem.CorrectCount)
			},
		},
		{
			name:           "Create Incorrect Study Session",
			path:           "/api/words/1/incorrect",
			method:         "POST",
			expectedStatus: http.StatusCreated,
			setup: func(db *gorm.DB) {
				// Reset database before each test
				if err := resetTestDB(db); err != nil {
					t.Fatalf("Failed to reset test database: %v", err)
				}

				// Create test data again after reset
				_, err = createTestWord(db, "테스트1")
				if err != nil {
					t.Fatalf("Failed to create test word: %v", err)
				}
			},
			validateBody: func(t *testing.T, body []byte) {
				var response map[string]interface{}
				assert.NoError(t, json.Unmarshal(body, &response))
				assert.Equal(t, "Study session created", response["message"])

				// Verify that a new StudySession record was created
				var studySessions []models.StudySession
				if err := db.Find(&studySessions).Error; err != nil {
					t.Fatalf("Failed to find study sessions: %v", err)
				}

				assert.Len(t, studySessions, 1)

				// Retrieve the associated WordReviewItem
				var wordReviewItem models.WordReviewItem
				if err := db.Where("study_session_id = ?", studySessions[0].ID).First(&wordReviewItem).Error; err != nil {
					t.Fatalf("Failed to find word review item: %v", err)
				}

				// Assert that the WordID and Correct values match the expected values
				assert.Equal(t, uint(1), wordReviewItem.WordID)
				// Correct is an integer (0 or 1)
				assert.Equal(t, 0, wordReviewItem.CorrectCount)
			},
		},
		{
			name:           "Create Study Session with Invalid Word ID",
			path:           "/api/words/invalid/correct",
			method:         "POST",
			expectedStatus: http.StatusBadRequest,
			setup: func(db *gorm.DB) {
				// No setup needed for invalid word ID
			},
			validateBody: nil,
		},
		{
			name:           "Test Get Study Statistics",
			path:           "/api/words/1/correct",
			method:         "GET",
			expectedStatus: http.StatusOK,
			setup: func(db *gorm.DB) {
				// Reset database before each test
				if err := resetTestDB(db); err != nil {
					t.Fatalf("Failed to reset test database: %v", err)
				}

				// Create test data again after reset
				word, err := createTestWord(db, "테스트1")
				if err != nil {
					t.Fatalf("Failed to create test word: %v", err)
				}

				// Create test study sessions HERE, inside the setup function
				createTestStudySession(db, 1, word.ID, true)
				createTestStudySession(db, 1, word.ID, false)
				createTestStudySession(db, 1, word.ID, true)
			},
			validateBody: func(t *testing.T, body []byte) {
				repo := repository.NewWordRepository(repository.NewBaseRepository(db))
				handler := NewWordHandler(repo)

				// Get the word ID (assuming it's 1, as in the path)
				wordID := uint(1)

				// Call the GetStudyStatistics function
				correctCount, wrongCount, err := handler.GetStudyStatistics(wordID)
				if err != nil {
					t.Fatalf("Failed to get study statistics: %v", err)
				}

				// Assert that the correct counts are returned
				assert.Equal(t, 2, correctCount)
				assert.Equal(t, 1, wrongCount)
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Reset database before each test
			if tt.setup != nil {
				tt.setup(db)
			}

			w := httptest.NewRecorder()
			req, _ := http.NewRequest(tt.method, tt.path, nil)
			router.ServeHTTP(w, req)

			assert.Equal(t, tt.expectedStatus, w.Code)
			if tt.validateBody != nil && w.Code == http.StatusCreated {
				tt.validateBody(t, w.Body.Bytes())
			}
		})
	}
}
