package handlers

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/repository"
	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
)

func TestSentencePracticeHandler_Integration(t *testing.T) {
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
	word, err := createTestWord(db, "테스트")
	if err != nil {
		t.Fatalf("Failed to create test word: %v", err)
	}

	// Setup router
	gin.SetMode(gin.TestMode)
	router := gin.New()
	baseRepo := repository.NewBaseRepository(db)
	wordRepo := repository.NewWordRepository(baseRepo)
	handler := NewSentencePracticeHandler(wordRepo)

	router.GET("/api/sentence_practice", handler.GetPracticeSentence)
	router.GET("/api/sentence_practice/examples", handler.GetSentenceExamples)

	// Test cases
	tests := []struct {
		name           string
		path           string
		expectedStatus int
		validateBody   func(t *testing.T, body []byte)
	}{
		{
			name:           "Get Practice Sentence",
			path:           "/api/sentence_practice",
			expectedStatus: http.StatusOK,
			validateBody: func(t *testing.T, body []byte) {
				var response struct {
					Word struct {
						Hangul       string   `json:"hangul"`
						Romanization string   `json:"romanization"`
						English      []string `json:"english"`
					} `json:"word"`
					ExampleSentence struct {
						Korean  string `json:"korean"`
						English string `json:"english"`
					} `json:"example_sentence"`
				}
				assert.NoError(t, json.Unmarshal(body, &response))
				assert.NotEmpty(t, response.Word.Hangul)
				assert.NotEmpty(t, response.ExampleSentence.Korean)
				assert.NotEmpty(t, response.ExampleSentence.English)
			},
		},
		{
			name:           "Get Sentence Examples - With Word",
			path:           "/api/sentence_practice/examples?word=" + word.Hangul,
			expectedStatus: http.StatusOK,
			validateBody: func(t *testing.T, body []byte) {
				var response struct {
					Word             string `json:"word"`
					ExampleSentences []struct {
						Korean  string `json:"korean"`
						English string `json:"english"`
					} `json:"example_sentences"`
				}
				assert.NoError(t, json.Unmarshal(body, &response))
				assert.Equal(t, word.Hangul, response.Word)
				assert.NotEmpty(t, response.ExampleSentences)
			},
		},
		{
			name:           "Get Sentence Examples - No Word Param",
			path:           "/api/sentence_practice/examples",
			expectedStatus: http.StatusBadRequest,
		},
		{
			name:           "Get Sentence Examples - Word Not Found",
			path:           "/api/sentence_practice/examples?word=nonexistent",
			expectedStatus: http.StatusNotFound,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Reset database before each test
			if err := resetTestDB(db); err != nil {
				t.Fatalf("Failed to reset test database: %v", err)
			}

			// Create test data again after reset
			word, err = createTestWord(db, "테스트")
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
