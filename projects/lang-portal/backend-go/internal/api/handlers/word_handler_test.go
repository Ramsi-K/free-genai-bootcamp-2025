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

	// Test cases
	tests := []struct {
		name           string
		path           string
		expectedStatus int
		validateBody   func(t *testing.T, body []byte)
	}{
		{
			name:           "List Words",
			path:           "/api/words",
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
					assert.NotEmpty(t, word.English)
					assert.NotEmpty(t, word.ExampleSentence.Korean)
					assert.NotEmpty(t, word.ExampleSentence.English)
					assert.NotZero(t, word.CreatedAt)
					assert.NotZero(t, word.UpdatedAt)
				}
			},
		},
		{
			name:           "List Words - Invalid Page",
			path:           "/api/words?page=invalid",
			expectedStatus: http.StatusBadRequest,
		},
		{
			name:           "List Words - Invalid Limit",
			path:           "/api/words?limit=0",
			expectedStatus: http.StatusBadRequest,
		},
		{
			name:           "List Words - Negative Page",
			path:           "/api/words?page=-1",
			expectedStatus: http.StatusBadRequest,
		},
		{
			name:           "Get Word",
			path:           "/api/words/1",
			expectedStatus: http.StatusOK,
			validateBody: func(t *testing.T, body []byte) {
				var word models.Word
				assert.NoError(t, json.Unmarshal(body, &word))
				assert.Equal(t, uint(1), word.ID)
				assert.Equal(t, "테스트1", word.Hangul)
				assert.Equal(t, "test", word.Romanization)
				assert.Equal(t, "noun", word.Type)
				assert.Equal(t, models.StringSlice{"test"}, word.English)
				assert.Equal(t, "Test Korean sentence", word.ExampleSentence.Korean)
				assert.Equal(t, "Test English sentence", word.ExampleSentence.English)
				assert.Equal(t, 0, word.StudyStatistics.CorrectCount)
				assert.Equal(t, 0, word.StudyStatistics.WrongCount)
				assert.NotZero(t, word.CreatedAt)
				assert.NotZero(t, word.UpdatedAt)
			},
		},
		{
			name:           "Get Non-existent Word",
			path:           "/api/words/999",
			expectedStatus: http.StatusNotFound,
		},
		{
			name:           "Get Word with Invalid ID",
			path:           "/api/words/invalid",
			expectedStatus: http.StatusBadRequest,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Reset database before each test
			if err := resetTestDB(db); err != nil {
				t.Fatalf("Failed to reset test database: %v", err)
			}

			// Create test data again after reset
			_, err = createTestWord(db, "테스트1")
			if err != nil {
				t.Fatalf("Failed to create test word: %v", err)
			}

			_, err = createTestWord(db, "테스트2")
			if err != nil {
				t.Fatalf("Failed to create test word: %v", err)
			}

			w := httptest.NewRecorder()
			req := httptest.NewRequest("GET", tt.path, nil)
			router.ServeHTTP(w, req)

			assert.Equal(t, tt.expectedStatus, w.Code)
			if tt.validateBody != nil && w.Code == http.StatusOK {
				tt.validateBody(t, w.Body.Bytes())
			}
		})
	}
}
