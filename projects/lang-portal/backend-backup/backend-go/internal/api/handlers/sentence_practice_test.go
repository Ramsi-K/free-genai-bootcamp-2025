package handlers

import (
	"encoding/json"
	"net/http"
	"testing"

	"github.com/Ramsi-K/free-genai-bootcamp-2025/projects/lang-portal/backend-go/internal/models"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestSentencePracticeHandler(t *testing.T) {
	t.Run("GetPracticeSentence", func(t *testing.T) {
		helper, err := newTestHelper(t)
		require.NoError(t, err)

		// Seed test data
		err = helper.seedTestData()
		require.NoError(t, err)

		// Test successful request
		w := performRequest(helper.router, "GET", "/api/sentence_practice", nil)
		assert.Equal(t, http.StatusOK, w.Code)

		var response map[string]interface{}
		err = json.Unmarshal(w.Body.Bytes(), &response)
		require.NoError(t, err)

		// Verify response structure
		assert.NotNil(t, response["sentence_id"])
		assert.NotNil(t, response["word"])
		assert.NotNil(t, response["example_sentence"])

		word := response["word"].(map[string]interface{})
		assert.NotEmpty(t, word["hangul"])
		assert.NotEmpty(t, word["romanization"])
		assert.NotEmpty(t, word["english"])
	})

	t.Run("SubmitSentenceAttempt", func(t *testing.T) {
		helper, err := newTestHelper(t)
		require.NoError(t, err)

		// Seed test data
		err = helper.seedTestData()
		require.NoError(t, err)

		// Get a word ID for testing
		w := performRequest(helper.router, "GET", "/api/words", nil)
		assert.Equal(t, http.StatusOK, w.Code)

		var response map[string]interface{}
		err = json.Unmarshal(w.Body.Bytes(), &response)
		require.NoError(t, err)

		words := response["words"].([]interface{})
		require.NotEmpty(t, words)
		word := words[0].(map[string]interface{})
		wordID := uint(word["id"].(float64))

		// Test correct attempt
		w = performRequest(helper.router, "POST", "/api/sentence_practice/attempt", map[string]interface{}{
			"sentence_id":      wordID,
			"user_translation": "나는 학교에 갑니다",
		})
		assert.Equal(t, http.StatusOK, w.Code)

		err = json.Unmarshal(w.Body.Bytes(), &response)
		require.NoError(t, err)
		assert.True(t, response["correct"].(bool))
		assert.Equal(t, "Correct! Well done!", response["message"])
		assert.NotEmpty(t, response["alternatives"])

		// Test incorrect attempt
		w = performRequest(helper.router, "POST", "/api/sentence_practice/attempt", map[string]interface{}{
			"sentence_id":      wordID,
			"user_translation": "Wrong translation",
		})
		assert.Equal(t, http.StatusOK, w.Code)

		err = json.Unmarshal(w.Body.Bytes(), &response)
		require.NoError(t, err)
		assert.False(t, response["correct"].(bool))
		assert.Equal(t, "Not quite right. Try again!", response["message"])

		// Test non-existent sentence ID
		w = performRequest(helper.router, "POST", "/api/sentence_practice/attempt", map[string]interface{}{
			"sentence_id":      999,
			"user_translation": "Test",
		})
		assert.Equal(t, http.StatusNotFound, w.Code)

		// Test missing required fields
		w = performRequest(helper.router, "POST", "/api/sentence_practice/attempt", map[string]interface{}{
			"sentence_id": wordID,
		})
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})

	t.Run("GetSentenceExamples", func(t *testing.T) {
		helper, err := newTestHelper(t)
		require.NoError(t, err)

		// Seed test data
		err = helper.seedTestData()
		require.NoError(t, err)

		// Test successful request
		w := performRequest(helper.router, "GET", "/api/sentence_practice/examples?word=학교", nil)
		assert.Equal(t, http.StatusOK, w.Code)

		var response map[string]interface{}
		err = json.Unmarshal(w.Body.Bytes(), &response)
		require.NoError(t, err)
		assert.Equal(t, "학교", response["word"])
		assert.NotEmpty(t, response["example_sentences"])

		// Test with romanization
		w = performRequest(helper.router, "GET", "/api/sentence_practice/examples?word=hakgyo", nil)
		assert.Equal(t, http.StatusOK, w.Code)

		err = json.Unmarshal(w.Body.Bytes(), &response)
		require.NoError(t, err)
		assert.Equal(t, "hakgyo", response["word"])
		assert.NotEmpty(t, response["example_sentences"])

		// Test missing word parameter
		w = performRequest(helper.router, "GET", "/api/sentence_practice/examples", nil)
		assert.Equal(t, http.StatusBadRequest, w.Code)

		// Test non-existent word
		w = performRequest(helper.router, "GET", "/api/sentence_practice/examples?word=nonexistent", nil)
		assert.Equal(t, http.StatusOK, w.Code)
		err = json.Unmarshal(w.Body.Bytes(), &response)
		require.NoError(t, err)
		assert.Empty(t, response["example_sentences"])
	})

	t.Run("GetSentenceStatistics", func(t *testing.T) {
		helper, err := newTestHelper(t)
		require.NoError(t, err)

		// Seed test data
		err = helper.seedTestData()
		require.NoError(t, err)

		// Test empty statistics
		w := performRequest(helper.router, "GET", "/api/sentence_practice/statistics", nil)
		assert.Equal(t, http.StatusOK, w.Code)

		var emptyStats map[string]interface{}
		err = json.Unmarshal(w.Body.Bytes(), &emptyStats)
		require.NoError(t, err)
		assert.Equal(t, float64(0), emptyStats["total_sentences_attempted"])
		assert.Equal(t, float64(0), emptyStats["correct_answers"])
		assert.Equal(t, float64(0), emptyStats["accuracy_rate"])

		// Create some attempts
		attempts := []models.SentencePracticeAttempt{
			{
				WordID:          1,
				UserTranslation: "나는 학교에 갑니다",
				Correct:         true,
			},
			{
				WordID:          1,
				UserTranslation: "Wrong translation",
				Correct:         false,
			},
		}

		err = helper.db.Create(&attempts).Error
		require.NoError(t, err)

		// Test statistics with data
		w = performRequest(helper.router, "GET", "/api/sentence_practice/statistics", nil)
		assert.Equal(t, http.StatusOK, w.Code)

		var stats map[string]interface{}
		err = json.Unmarshal(w.Body.Bytes(), &stats)
		require.NoError(t, err)
		assert.Equal(t, float64(2), stats["total_sentences_attempted"])
		assert.Equal(t, float64(1), stats["correct_answers"])
		assert.Equal(t, float64(50), stats["accuracy_rate"])
	})
}
