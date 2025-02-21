package handlers

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strconv"
	"testing"

	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/repository"
	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
	"gorm.io/gorm"
)

// setupRouter is a placeholder for the actual setupRouter function
// In a real application, this function would initialize the router and
// define the API endpoints.
func setupRouter(db *gorm.DB) *gin.Engine {
	router := gin.Default()

	// Initialize repositories
	wordRepo := repository.NewWordRepository(repository.NewBaseRepository(db))

	// Create a new SentencePracticeHandler, passing in the database connection
	handler := NewSentencePracticeHandler(wordRepo, db)

	// Define the API routes and register the handler
	router.GET("/api/sentence_practice/examples", handler.GetSentencePracticeExamples)

	return router
}

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

	// Setup router
	router := setupRouter(db)

	// Define test cases
	var wordID uint
	word, err := createTestWord(db, "테스트")
	if err != nil {
		t.Fatalf("Failed to create test word: %v", err)
	}
	wordID = word.ID

	tests := []struct {
		name           string
		path           string
		expectedStatus int
		validateBody   func(*testing.T, []byte)
	}{
		{
			name:           "GetSentenceExamples - Valid Word ID",
			path:           "/api/sentence_practice/examples?word_id=" + strconv.FormatUint(uint64(wordID), 10),
			expectedStatus: http.StatusOK,
			validateBody: func(t *testing.T, body []byte) {
				var response PracticeSentenceResponse
				err := json.Unmarshal(body, &response)
				assert.NoError(t, err)
				assert.Equal(t, "테스트", response.Word)
				//assert.Equal(t, "Test sentence in Korean", response.ExampleSentences[0])
				//assert.Equal(t, "Test sentence in English", response.ExampleSentences[1])
			},
		},
		{
			name:           "GetSentenceExamples - Invalid Word ID",
			path:           "/api/sentence_practice/examples?word_id=invalid",
			expectedStatus: http.StatusBadRequest,
		},
		{
			name:           "GetSentenceExamples - Word Not Found",
			path:           "/api/sentence_practice/examples?word_id=999",
			expectedStatus: http.StatusNotFound,
		},
	}

	// Run test cases
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Reset database before each test
			err = resetTestDB(db)
			if err != nil {
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
