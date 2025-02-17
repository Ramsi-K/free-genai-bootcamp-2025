package handlers

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"os"
	"testing"

	"github.com/Ramsi-K/free-genai-bootcamp-2025/tree/main/projects/lang-portal/backend-go/internal/models"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestWordHandler(t *testing.T) {
	t.Run("List", func(t *testing.T) {
		helper, err := newTestHelper(t)
		require.NoError(t, err)

		handler := NewWordHandler(helper.db)
		helper.router.GET("/api/words", handler.List)

		// Seed test data
		err = helper.seedTestData()
		require.NoError(t, err)

		// Test successful list request
		w := performRequest(helper.router, "GET", "/api/words", nil)
		assert.Equal(t, http.StatusOK, w.Code)

		var response struct {
			Words      []models.Word `json:"words"`
			Pagination struct {
				CurrentPage int   `json:"current_page"`
				TotalPages  int   `json:"total_pages"`
				TotalItems  int64 `json:"total_items"`
				PerPage     int   `json:"per_page"`
			} `json:"pagination"`
		}
		err = json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)
		assert.Len(t, response.Words, 2)
		assert.Equal(t, "학교", response.Words[0].Hangul)
		assert.Equal(t, "hakgyo", response.Words[0].Romanization)

		// Test pagination
		w = performRequest(helper.router, "GET", "/api/words?page=1&limit=1", nil)
		assert.Equal(t, http.StatusOK, w.Code)
		err = json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)
		assert.Len(t, response.Words, 1)
		assert.Equal(t, 1, response.Pagination.CurrentPage)
		assert.Equal(t, 2, response.Pagination.TotalPages)

		// Test invalid page number
		w = performRequest(helper.router, "GET", "/api/words?page=0", nil)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})

	t.Run("Get", func(t *testing.T) {
		helper, err := newTestHelper(t)
		require.NoError(t, err)

		handler := NewWordHandler(helper.db)
		helper.router.GET("/api/words/:id", handler.Get)

		// Seed test data
		err = helper.seedTestData()
		require.NoError(t, err)

		// Test successful get request
		w := performRequest(helper.router, "GET", "/api/words/1", nil)
		assert.Equal(t, http.StatusOK, w.Code)

		var word models.Word
		err = json.Unmarshal(w.Body.Bytes(), &word)
		assert.NoError(t, err)
		assert.Equal(t, "학교", word.Hangul)
		assert.Equal(t, "hakgyo", word.Romanization)
		assert.Equal(t, "그는 학교에서 저보다 한 학년 위였어요.", word.Example.Korean)

		// Test non-existent word
		w = performRequest(helper.router, "GET", "/api/words/999", nil)
		assert.Equal(t, http.StatusNotFound, w.Code)

		// Test invalid ID format
		w = performRequest(helper.router, "GET", "/api/words/invalid", nil)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})
}

func TestWordHandler_List(t *testing.T) {
	// Test data
	testWords := []models.Word{
		{
			Hangul:         "학교",
			Romanization:   "hakgyo",
			English:        []string{"school"},
			Type:           "noun",
			ExampleKorean:  "나는 학교에 갑니다",
			ExampleEnglish: "I go to school",
		},
		{
			Hangul:         "사과",
			Romanization:   "sagwa",
			English:        []string{"apple"},
			Type:           "noun",
			ExampleKorean:  "사과를 먹습니다",
			ExampleEnglish: "I eat an apple",
		},
	}

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
			db := setupTestDB(t, testWords)
			handler := NewWordHandler(db)
			router := setupTestRouter(handler)

			// Create request
			w := httptest.NewRecorder()
			req, _ := http.NewRequest("GET", "/api/words"+tt.query, nil)
			router.ServeHTTP(w, req)

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
	// Setup fresh database once for all subtests
	db := createMockDB(t)
	wordID := os.Getenv("TEST_WORD_ID")

	tests := []struct {
		name           string
		wordID         string
		expectedStatus int
		expectedHangul string
	}{
		{
			name:           "Existing word",
			wordID:         wordID,
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
			handler := NewWordHandler(db)
			router := setupTestRouter(handler)

			// Create request
			w := httptest.NewRecorder()
			req, _ := http.NewRequest("GET", fmt.Sprintf("/api/words/%s", tt.wordID), nil)
			router.ServeHTTP(w, req)

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
