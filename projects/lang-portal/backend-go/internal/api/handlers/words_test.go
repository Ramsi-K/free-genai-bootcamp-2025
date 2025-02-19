package handlers

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

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

		var response map[string]interface{}
		err = json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)

		words := response["words"].([]interface{})
		assert.Len(t, words, 2)

		// Check first word
		word := words[0].(map[string]interface{})
		assert.Equal(t, "학교", word["hangul"])
		assert.Equal(t, "hakgyo", word["romanization"])
		assert.Equal(t, []interface{}{"school"}, word["english"])
		assert.Equal(t, "noun", word["type"])
		example := word["example"].(map[string]interface{})
		assert.Equal(t, "나는 학교에 갑니다", example["korean"])
		assert.Equal(t, "I go to school", example["english"])
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

		var word map[string]interface{}
		err = json.Unmarshal(w.Body.Bytes(), &word)
		assert.NoError(t, err)

		// Check word details
		assert.Equal(t, "학교", word["hangul"])
		assert.Equal(t, "hakgyo", word["romanization"])
		assert.Equal(t, []interface{}{"school"}, word["english"])
		assert.Equal(t, "noun", word["type"])
		example := word["example"].(map[string]interface{})
		assert.Equal(t, "나는 학교에 갑니다", example["korean"])
		assert.Equal(t, "I go to school", example["english"])

		// Test non-existent word
		w = performRequest(helper.router, "GET", "/api/words/999", nil)
		assert.Equal(t, http.StatusNotFound, w.Code)

		// Test invalid ID format
		w = performRequest(helper.router, "GET", "/api/words/invalid", nil)
		assert.Equal(t, http.StatusBadRequest, w.Code)
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
				var response map[string]interface{}
				err = json.Unmarshal(w.Body.Bytes(), &response)
				assert.NoError(t, err)

				words := response["words"].([]interface{})
				assert.Len(t, words, tt.expectedLen)

				if tt.expectedLen > 0 {
					word := words[0].(map[string]interface{})
					assert.Equal(t, tt.expectedFirst, word["hangul"])
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
				var word map[string]interface{}
				err = json.Unmarshal(w.Body.Bytes(), &word)
				assert.NoError(t, err)
				assert.Equal(t, tt.expectedHangul, word["hangul"])
			}
		})
	}
}
