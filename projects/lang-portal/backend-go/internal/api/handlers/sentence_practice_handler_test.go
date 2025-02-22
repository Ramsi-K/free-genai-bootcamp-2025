package handlers

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/models"
	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/repository"
	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"gorm.io/gorm"
)

// MockWordRepository mocks the WordRepository interface
type MockWordRepository struct {
	mock.Mock
}

func (m *MockWordRepository) ListWords(page, limit int) ([]models.Word, int64, error) {
	args := m.Called(page, limit)
	return args.Get(0).([]models.Word), args.Get(1).(int64), args.Error(2)
}

func (m *MockWordRepository) GetWord(id uint) (*models.Word, error) {
	args := m.Called(id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*models.Word), args.Error(1)
}

func (m *MockWordRepository) GetWordsByGroup(groupID uint) ([]models.Word, error) {
	args := m.Called(groupID)
	return args.Get(0).([]models.Word), args.Error(1)
}

func (m *MockWordRepository) GetDB() *gorm.DB {
	args := m.Called()
	return args.Get(0).(*gorm.DB)
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

	// Create test data for a word with sentence
	// Ensure we have a word with ID 1
	word, err := createTestWord(db, "테스트")
	if err != nil {
		t.Fatalf("Failed to create test word: %v", err)
	}

	// Setup router
	gin.SetMode(gin.TestMode)
	router := gin.New()
	wordRepo := repository.NewWordRepository(repository.NewBaseRepository(db))
	handler := NewSentencePracticeHandler(wordRepo, db)

	router.GET("/api/sentence_practice", handler.GetSentencePractice)
	router.POST("/api/sentence_practice/attempt", handler.PostSentencePracticeAttempt)
	router.GET("/api/sentence_practice/examples", handler.GetSentencePracticeExamples)
	router.GET("/api/sentence_practice/statistics", handler.GetSentencePracticeStatistics)

	// Create test activity (required for creating study sessions)
	_, err = createTestActivity(db, "Sentence Practice")
	if err != nil {
		t.Fatalf("Failed to create test activity: %v", err)
	}

	// Test cases
	tests := []struct {
		name           string
		method         string
		path           string
		body           interface{}
		expectedStatus int
		validateBody   func(t *testing.T, body []byte)
	}{
		{
			name:           "Get Random Sentence Practice",
			method:         "GET",
			path:           "/api/sentence_practice",
			expectedStatus: http.StatusOK,
			validateBody: func(t *testing.T, body []byte) {
				var response PracticeSentenceResponse
				err := json.Unmarshal(body, &response)
				assert.NoError(t, err)
				assert.NotEmpty(t, response.Word)
				assert.NotEmpty(t, response.ExampleSentences)
			},
		},
		{
			name:           "Get Sentence Examples",
			method:         "GET",
			path:           "/api/sentence_practice/examples?word_id=1", // Will be updated in the test
			expectedStatus: http.StatusOK,
			validateBody: func(t *testing.T, body []byte) {
				var response PracticeSentenceResponse
				err := json.Unmarshal(body, &response)
				assert.NoError(t, err)
				assert.NotEmpty(t, response.Word)
				assert.NotNil(t, response.ExampleSentences)
			},
		},
		{
			name:           "Get Sentence Examples - Word Not Found",
			method:         "GET",
			path:           "/api/sentence_practice/examples?word_id=999",
			expectedStatus: http.StatusNotFound,
		},
		{
			name:           "Get Sentence Examples - Invalid ID",
			method:         "GET",
			path:           "/api/sentence_practice/examples?word_id=invalid",
			expectedStatus: http.StatusBadRequest,
		},
		{
			name:           "Get Sentence Examples - Missing ID",
			method:         "GET",
			path:           "/api/sentence_practice/examples",
			expectedStatus: http.StatusBadRequest,
		},
		{
			name:   "Post Sentence Practice Attempt",
			method: "POST",
			path:   "/api/sentence_practice/attempt",
			body: SentencePracticeRequest{
				WordID:      word.ID,
				UserAnswer:  "테스트 문장입니다.",
				CorrectText: "테스트 문장입니다.",
			},
			expectedStatus: http.StatusOK,
			validateBody: func(t *testing.T, body []byte) {
				var response SentencePracticeAttemptResponse
				err := json.Unmarshal(body, &response)
				assert.NoError(t, err)
				assert.Equal(t, true, response.IsCorrect)
				assert.Equal(t, float64(100), response.Score)
				assert.Equal(t, "테스트 문장입니다.", response.CorrectAnswer)
			},
		},
		{
			name:   "Post Sentence Practice Attempt - Partial Match",
			method: "POST",
			path:   "/api/sentence_practice/attempt",
			body: SentencePracticeRequest{
				WordID:      word.ID,
				UserAnswer:  "테스트",
				CorrectText: "테스트 문장입니다.",
			},
			expectedStatus: http.StatusOK,
			validateBody: func(t *testing.T, body []byte) {
				var response SentencePracticeAttemptResponse
				err := json.Unmarshal(body, &response)
				assert.NoError(t, err)
				assert.Equal(t, false, response.IsCorrect)
				assert.Less(t, response.Score, float64(100))
				assert.Equal(t, "테스트 문장입니다.", response.CorrectAnswer)
			},
		},
		{
			name:   "Post Sentence Practice Attempt - Invalid Word",
			method: "POST",
			path:   "/api/sentence_practice/attempt",
			body: SentencePracticeRequest{
				WordID:      999,
				UserAnswer:  "테스트",
				CorrectText: "테스트 문장입니다.",
			},
			expectedStatus: http.StatusNotFound,
		},
		{
			name:           "Post Sentence Practice Attempt - Invalid Request",
			method:         "POST",
			path:           "/api/sentence_practice/attempt",
			body:           "invalid",
			expectedStatus: http.StatusBadRequest,
		},
		{
			name:           "Get Sentence Practice Statistics",
			method:         "GET",
			path:           "/api/sentence_practice/statistics",
			expectedStatus: http.StatusOK,
			validateBody: func(t *testing.T, body []byte) {
				var stats SentencePracticeStatistics
				err := json.Unmarshal(body, &stats)
				assert.NoError(t, err)
				// Don't validate specific stats values as they will depend on database state
				assert.GreaterOrEqual(t, stats.TotalAttempts, 0)
				assert.GreaterOrEqual(t, stats.CorrectAttempts, 0)
				assert.GreaterOrEqual(t, stats.SuccessRate, float64(0))
				assert.GreaterOrEqual(t, stats.AverageScore, float64(0))
			},
		},
	}

	// Update test paths that reference word ID
	for i := range tests {
		if tests[i].path == "/api/sentence_practice/examples?word_id=1" {
			tests[i].path = fmt.Sprintf("/api/sentence_practice/examples?word_id=%d", word.ID)
		}
		if bodyStruct, ok := tests[i].body.(SentencePracticeRequest); ok {
			bodyStruct.WordID = word.ID
			if bodyStruct.CorrectText == "테스트 문장입니다." {
				bodyStruct.CorrectText = word.Sentences[0].Korean
			}
			tests[i].body = bodyStruct
		}
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			var req *http.Request
			var bodyBytes []byte

			if tt.body != nil {
				var err error
				if s, ok := tt.body.(string); ok {
					bodyBytes = []byte(s)
				} else {
					bodyBytes, err = json.Marshal(tt.body)
					if err != nil {
						t.Fatalf("Failed to marshal request body: %v", err)
					}
				}
				req = httptest.NewRequest(tt.method, tt.path, bytes.NewBuffer(bodyBytes))
				req.Header.Set("Content-Type", "application/json")
			} else {
				req = httptest.NewRequest(tt.method, tt.path, nil)
			}

			w := httptest.NewRecorder()
			router.ServeHTTP(w, req)

			assert.Equal(t, tt.expectedStatus, w.Code)
			if tt.validateBody != nil && w.Code == tt.expectedStatus && w.Code != http.StatusBadRequest && w.Code != http.StatusNotFound {
				tt.validateBody(t, w.Body.Bytes())
			}
		})
	}
}
