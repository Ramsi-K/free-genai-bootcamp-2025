package handlers

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strconv"
	"testing"

	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/repository"
	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
)

func TestSentencePracticeHandler_Integration(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test")
	}

	// Setup test DB
	db, err := setupTestDB()
	assert.NoError(t, err)
	defer cleanupTestDB(db)

	// Create a test word with at least one sentence.
	// createTestWord is assumed to create a word along with at least one sentence.
	word, err := createTestWord(db, "테스트")
	assert.NoError(t, err)
	assert.NotZero(t, word.ID)
	assert.NotEmpty(t, word.Sentences)

	// Setup router, repository, and handler
	gin.SetMode(gin.TestMode)
	router := gin.New()
	wordRepo := repository.NewWordRepository(repository.NewBaseRepository(db))
	handler := NewSentencePracticeHandler(wordRepo, db)

	// Register endpoints used in these tests
	router.GET("/api/sentence_practice/examples", handler.GetSentencePracticeExamples)
	router.POST("/api/sentence_practice/attempt", handler.PostSentencePracticeAttempt)

	// --- Test: Get Sentence Examples ---
	url := "/api/sentence_practice/examples?word_id=" + strconv.Itoa(int(word.ID))
	req := httptest.NewRequest("GET", url, nil)
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)
	assert.Equal(t, http.StatusOK, w.Code, "Expected status 200 for Get_Sentence_Examples")

	// --- Test: Post Sentence Practice Attempt - Exact Match ---
	exactAttempt := SentencePracticeRequest{
		WordID:      word.ID,
		UserAnswer:  word.Sentences[0].Korean,
		CorrectText: word.Sentences[0].Korean,
	}
	reqBody, err := json.Marshal(exactAttempt)
	assert.NoError(t, err)
	req = httptest.NewRequest("POST", "/api/sentence_practice/attempt", bytes.NewBuffer(reqBody))
	req.Header.Set("Content-Type", "application/json")
	w = httptest.NewRecorder()
	router.ServeHTTP(w, req)
	assert.Equal(t, http.StatusOK, w.Code, "Expected status 200 for exact match attempt")

	// --- Test: Post Sentence Practice Attempt - Partial Match ---
	partialAttempt := SentencePracticeRequest{
		WordID:      word.ID,
		UserAnswer:  "부분답변", // a partial answer
		CorrectText: word.Sentences[0].Korean,
	}
	reqBody, err = json.Marshal(partialAttempt)
	assert.NoError(t, err)
	req = httptest.NewRequest("POST", "/api/sentence_practice/attempt", bytes.NewBuffer(reqBody))
	req.Header.Set("Content-Type", "application/json")
	w = httptest.NewRecorder()
	router.ServeHTTP(w, req)
	// Expect a 200 status even for partial match
	assert.Equal(t, http.StatusOK, w.Code, "Expected status 200 for partial match attempt")

	// --- Test: Post Sentence Practice Attempt - Invalid Word ---
	invalidAttempt := SentencePracticeRequest{
		WordID:      9999, // non-existent word ID
		UserAnswer:  "any answer",
		CorrectText: "any correct text",
	}
	reqBody, err = json.Marshal(invalidAttempt)
	assert.NoError(t, err)
	req = httptest.NewRequest("POST", "/api/sentence_practice/attempt", bytes.NewBuffer(reqBody))
	req.Header.Set("Content-Type", "application/json")
	w = httptest.NewRecorder()
	router.ServeHTTP(w, req)
	assert.Equal(t, http.StatusNotFound, w.Code, "Expected status 404 for invalid word attempt")
}
