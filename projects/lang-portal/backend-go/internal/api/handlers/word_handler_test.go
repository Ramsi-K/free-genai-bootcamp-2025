package handlers

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/models"
	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/repository"
	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
)

func TestWordHandler_Integration(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test")
	}

	// Setup
	db, err := setupTestDB()
	assert.NoError(t, err)
	if err != nil {
		t.Fatalf("Failed to setup test database: %v", err)
	}
	defer cleanupTestDB(db)

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
		setup          func(db *models.Word)
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
				err := json.Unmarshal(body, &response)
				assert.NoError(t, err)
				assert.Len(t, response.Data, 2)
				assert.Equal(t, 1, response.Meta.CurrentPage)
				assert.Equal(t, 10, response.Meta.PerPage)
				assert.Equal(t, int64(2), response.Meta.Total)

				// Validate the English translations are correctly loaded
				for _, word := range response.Data {
					assert.NotEmpty(t, word.English)
					assert.Len(t, word.Sentences, 1)
				}
			},
		},
		{
			name:           "Get Word",
			path:           "/api/words/1",
			method:         "GET",
			expectedStatus: http.StatusOK,
			validateBody: func(t *testing.T, body []byte) {
				var word models.Word
				err := json.Unmarshal(body, &word)
				assert.NoError(t, err)
				assert.Equal(t, uint(1), word.ID)
				assert.Equal(t, "테스트1", word.Hangul)
				assert.NotEmpty(t, word.English)
				assert.Len(t, word.Sentences, 1)
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
			validateBody: func(t *testing.T, body []byte) {
				var response map[string]interface{}
				err := json.Unmarshal(body, &response)
				assert.NoError(t, err)
				assert.Equal(t, "Study session created", response["message"])

				// Verify a session was created
				var sessions []models.StudySession
				err = db.Find(&sessions).Error
				assert.NoError(t, err)
				assert.NotEmpty(t, sessions)

				// Verify word review
				var reviews []models.WordReviewItem
				err = db.Where("word_id = ?", 1).Find(&reviews).Error
				assert.NoError(t, err)
				assert.NotEmpty(t, reviews)

				// Verify the last review is correct
				lastReview := reviews[len(reviews)-1]
				assert.Equal(t, uint(1), lastReview.WordID)
				assert.Equal(t, 1, lastReview.CorrectCount)
			},
		},
		{
			name:           "Create Incorrect Study Session",
			path:           "/api/words/1/incorrect",
			method:         "POST",
			expectedStatus: http.StatusCreated,
			validateBody: func(t *testing.T, body []byte) {
				var response map[string]interface{}
				err := json.Unmarshal(body, &response)
				assert.NoError(t, err)
				assert.Equal(t, "Study session created", response["message"])

				// Verify a session was created
				var sessions []models.StudySession
				err = db.Find(&sessions).Error
				assert.NoError(t, err)
				assert.NotEmpty(t, sessions)

				// Verify word review
				var reviews []models.WordReviewItem
				err = db.Where("word_id = ?", 1).Find(&reviews).Error
				assert.NoError(t, err)
				assert.NotEmpty(t, reviews)

				// Verify the last review is incorrect
				lastReview := reviews[len(reviews)-1]
				assert.Equal(t, uint(1), lastReview.WordID)
				assert.Equal(t, 0, lastReview.CorrectCount)
			},
		},
		{
			name:           "Create Study Session with Invalid Word ID",
			path:           "/api/words/invalid/correct",
			method:         "POST",
			expectedStatus: http.StatusBadRequest,
		},
		{
			name:           "Create Study Session with Non-existent Word ID",
			path:           "/api/words/999/correct",
			method:         "POST",
			expectedStatus: http.StatusNotFound,
		},
		{
			name:           "List Words - Pagination",
			path:           "/api/words?page=1&limit=1",
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
				err := json.Unmarshal(body, &response)
				assert.NoError(t, err)
				assert.Len(t, response.Data, 1)
				assert.Equal(t, 1, response.Meta.CurrentPage)
				assert.Equal(t, 1, response.Meta.PerPage)
				assert.Equal(t, int64(2), response.Meta.Total)
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Reset database before each test
			if err := resetTestDB(db); err != nil {
				t.Fatalf("Failed to reset test database: %v", err)
			}

			// Create test data
			word1, err := createTestWord(db, "테스트1")
			assert.NoError(t, err, "Failed to create test word")
			if err != nil {
				t.Fatalf("Failed to create test word: %v", err)
			}
			log.Printf("Created test word with ID: %d", word1.ID)

			// More detailed assertions
			assert.NotNil(t, word1, "Test word should not be nil")
			assert.NotZero(t, word1.ID, "Test word should have a valid ID")
			assert.NotEmpty(t, word1.Hangul, "Test word should have a Hangul value")
			assert.NotEmpty(t, word1.English, "Test word should have English translations")
			assert.NotEmpty(t, word1.Sentences, "Test word should have sentences")

			_, err = createTestWord(db, "테스트2")
			if err != nil {
				t.Fatalf("Failed to create test word: %v", err)
			}

			// Make sure study activity exists for sessions
			_, err = createTestActivity(db, "Test Activity")
			if err != nil {
				t.Fatalf("Failed to create test activity: %v", err)
			}

			if tt.setup != nil {
				tt.setup(word1)
			}

			// Make the request
			w := httptest.NewRecorder()
			req, _ := http.NewRequest(tt.method, tt.path, nil)
			router.ServeHTTP(w, req)

			// Verify response
			if w.Code != tt.expectedStatus {
				t.Errorf("Expected status %d but got %d: %s", tt.expectedStatus, w.Code, w.Body.String())
			}

			assert.Equal(t, tt.expectedStatus, w.Code)
			if tt.validateBody != nil && w.Code < 400 {
				tt.validateBody(t, w.Body.Bytes())
			}
		})
	}
}

// TestWordHandler_InvalidParams tests handling of invalid query parameters
func TestWordHandler_InvalidParams(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test")
	}

	// Setup
	db, err := setupTestDB()
	if err != nil {
		t.Fatalf("Failed to setup test database: %v", err)
	}
	defer cleanupTestDB(db)

	// Setup router
	gin.SetMode(gin.TestMode)
	router := gin.New()
	repo := repository.NewWordRepository(repository.NewBaseRepository(db))
	handler := NewWordHandler(repo)

	router.GET("/api/words", handler.ListWords)

	// Create test data
	_, err = createTestWord(db, "테스트1")
	if err != nil {
		t.Fatalf("Failed to create test word: %v", err)
	}

	// Test cases
	tests := []struct {
		name           string
		path           string
		expectedStatus int
	}{
		{
			name:           "Invalid Page - Negative",
			path:           "/api/words?page=-1",
			expectedStatus: http.StatusBadRequest,
		},
		{
			name:           "Invalid Page - Zero",
			path:           "/api/words?page=0",
			expectedStatus: http.StatusBadRequest,
		},
		{
			name:           "Invalid Page - Not a Number",
			path:           "/api/words?page=abc",
			expectedStatus: http.StatusBadRequest,
		},
		{
			name:           "Invalid Limit - Negative",
			path:           "/api/words?limit=-1",
			expectedStatus: http.StatusBadRequest,
		},
		{
			name:           "Invalid Limit - Zero",
			path:           "/api/words?limit=0",
			expectedStatus: http.StatusBadRequest,
		},
		{
			name:           "Invalid Limit - Not a Number",
			path:           "/api/words?limit=abc",
			expectedStatus: http.StatusBadRequest,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			w := httptest.NewRecorder()
			req, _ := http.NewRequest("GET", tt.path, nil)
			router.ServeHTTP(w, req)

			assert.Equal(t, tt.expectedStatus, w.Code, fmt.Sprintf("Expected status %d but got %d: %s", tt.expectedStatus, w.Code, w.Body.String()))
		})
	}
}
