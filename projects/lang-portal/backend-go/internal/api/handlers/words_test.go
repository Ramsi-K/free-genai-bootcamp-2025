package handlers

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/Ramsi-K/free-genai-bootcamp-2025/tree/main/projects/lang-portal/backend-go/internal/models"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestWordHandler(t *testing.T) {
	t.Run("List", func(t *testing.T) {
		// Setup
		helper, err := newTestHelper(t)
		require.NoError(t, err)

		// Seed test data
		err = helper.seedTestData()
		require.NoError(t, err)

		// Create request
		w := performRequest(helper.router, "GET", "/api/words", nil)

		// Assert response
		assert.Equal(t, http.StatusOK, w.Code)

		var response []models.Word
		err = json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)
		assert.Len(t, response, 2)

		// Check first word
		assert.Equal(t, "학교", response[0].Hangul)
		assert.Equal(t, "hakgyo", response[0].Romanization)
		assert.Equal(t, []string{"school"}, response[0].English)
		assert.Equal(t, "noun", response[0].Type)
		assert.Equal(t, "나는 학교에 갑니다", response[0].ExampleSentence.Korean)
		assert.Equal(t, "I go to school", response[0].ExampleSentence.English)
	})

	t.Run("Get", func(t *testing.T) {
		// Setup
		helper, err := newTestHelper(t)
		require.NoError(t, err)

		// Seed test data
		err = helper.seedTestData()
		require.NoError(t, err)

		// Create request
		w := performRequest(helper.router, "GET", "/api/words/1", nil)

		// Assert response
		assert.Equal(t, http.StatusOK, w.Code)

		var response models.Word
		err = json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)

		// Check word details
		assert.Equal(t, "학교", response.Hangul)
		assert.Equal(t, "hakgyo", response.Romanization)
		assert.Equal(t, []string{"school"}, response.English)
		assert.Equal(t, "noun", response.Type)
		assert.Equal(t, "나는 학교에 갑니다", response.ExampleSentence.Korean)
		assert.Equal(t, "I go to school", response.ExampleSentence.English)
	})
}

func TestWordHandler_List(t *testing.T) {
	tests := []struct {
		name           string
		query          string
		expectedStatus int
		expectedLen    int
		expectedFirst  string
		expectedError  string
	}{
		{
			name:           "Default pagination",
			query:          "?page=1&limit=2",
			expectedStatus: http.StatusOK,
			expectedLen:    2,
			expectedFirst:  "학교",
		},
		{
			name:           "Sort by hangul desc",
			query:          "?sort_by=hangul&order=desc&limit=2",
			expectedStatus: http.StatusOK,
			expectedLen:    2,
			expectedFirst:  "학교",
		},
		{
			name:           "Invalid page number",
			query:          "?page=invalid",
			expectedStatus: http.StatusBadRequest,
			expectedError:  "Invalid page number",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Setup fresh database for each test
			helper, err := newTestHelper(t)
			require.NoError(t, err)

			// Seed test data
			err = helper.seedTestData()
			require.NoError(t, err)

			// Create request
			w := httptest.NewRecorder()
			req, _ := http.NewRequest("GET", "/api/words"+tt.query, nil)
			helper.router.ServeHTTP(w, req)

			// Assert status code
			assert.Equal(t, tt.expectedStatus, w.Code)

			if tt.expectedStatus == http.StatusOK {
				words, err := parseWordList(w)
				assert.NoError(t, err)
				assert.Len(t, words, tt.expectedLen)

				if tt.expectedLen > 0 {
					assert.Equal(t, tt.expectedFirst, words[0]["hangul"])
				}
			} else if tt.expectedError != "" {
				response, err := parseResponse(w)
				assert.NoError(t, err)
				assert.Equal(t, tt.expectedError, response["error"])
			}
		})
	}
}

func TestWordHandler_Get(t *testing.T) {
	tests := []struct {
		name           string
		wordID         string
		expectedStatus int
		expectedHangul string
	}{
		{
			name:           "Existing word",
			wordID:         "1",
			expectedStatus: http.StatusOK,
			expectedHangul: "학교",
		},
		{
			name:           "Non-existent word",
			wordID:         "999",
			expectedStatus: http.StatusNotFound,
			expectedHangul: "",
		},
		{
			name:           "Invalid ID",
			wordID:         "invalid",
			expectedStatus: http.StatusBadRequest,
			expectedHangul: "",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Setup fresh database for each test
			helper, err := newTestHelper(t)
			require.NoError(t, err)

			// Seed test data if testing existing word
			if tt.expectedStatus == http.StatusOK {
				err = helper.seedTestData()
				require.NoError(t, err)
			}

			// Create request
			w := httptest.NewRecorder()
			req, _ := http.NewRequest("GET", "/api/words/"+tt.wordID, nil)
			helper.router.ServeHTTP(w, req)

			// Assert status code
			assert.Equal(t, tt.expectedStatus, w.Code)

			if tt.expectedStatus == http.StatusOK {
				// Parse response
				response, err := parseResponse(w)
				assert.NoError(t, err)
				assert.Equal(t, tt.expectedHangul, response["hangul"])
			}
		})
	}
}
