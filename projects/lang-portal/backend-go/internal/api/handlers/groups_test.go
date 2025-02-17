package handlers

import (
	"encoding/json"
	"net/http"
	"testing"

	"github.com/Ramsi-K/free-genai-bootcamp-2025/tree/main/projects/lang-portal/backend-go/internal/models"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestGroupHandler(t *testing.T) {
	t.Run("List", func(t *testing.T) {
		helper, err := newTestHelper(t)
		require.NoError(t, err)

		handler := NewGroupHandler(helper.db)
		helper.router.GET("/api/groups", handler.List)

		// Seed test data
		err = helper.seedTestData()
		require.NoError(t, err)

		// Test successful list request
		w := performRequest(helper.router, "GET", "/api/groups", nil)
		assert.Equal(t, http.StatusOK, w.Code)

		var groups []models.Group
		err = json.Unmarshal(w.Body.Bytes(), &groups)
		assert.NoError(t, err)
		assert.Len(t, groups, 2)
		assert.Equal(t, "School-related Words", groups[0].Name)
		assert.Equal(t, 2, groups[0].WordsCount)
	})

	t.Run("Get", func(t *testing.T) {
		helper, err := newTestHelper(t)
		require.NoError(t, err)

		handler := NewGroupHandler(helper.db)
		helper.router.GET("/api/groups/:id", handler.Get)

		// Seed test data
		err = helper.seedTestData()
		require.NoError(t, err)

		// Test successful get request
		w := performRequest(helper.router, "GET", "/api/groups/1", nil)
		assert.Equal(t, http.StatusOK, w.Code)

		var group models.Group
		err = json.Unmarshal(w.Body.Bytes(), &group)
		assert.NoError(t, err)
		assert.Equal(t, "School-related Words", group.Name)
		assert.Equal(t, 2, group.WordsCount)

		// Test non-existent group
		w = performRequest(helper.router, "GET", "/api/groups/999", nil)
		assert.Equal(t, http.StatusNotFound, w.Code)

		// Test invalid ID format
		w = performRequest(helper.router, "GET", "/api/groups/invalid", nil)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})

	t.Run("GetWords", func(t *testing.T) {
		helper, err := newTestHelper(t)
		require.NoError(t, err)

		handler := NewGroupHandler(helper.db)
		helper.router.GET("/api/groups/:id/words", handler.GetWords)

		// Seed test data
		err = helper.seedTestData()
		require.NoError(t, err)

		// Test successful get words request
		w := performRequest(helper.router, "GET", "/api/groups/1/words", nil)
		assert.Equal(t, http.StatusOK, w.Code)

		var words []models.Word
		err = json.Unmarshal(w.Body.Bytes(), &words)
		assert.NoError(t, err)
		assert.Len(t, words, 2)
		assert.Equal(t, "학교", words[0].Hangul)
		assert.Equal(t, "hakgyo", words[0].Romanization)

		// Test non-existent group
		w = performRequest(helper.router, "GET", "/api/groups/999/words", nil)
		assert.Equal(t, http.StatusNotFound, w.Code)

		// Test invalid ID format
		w = performRequest(helper.router, "GET", "/api/groups/invalid/words", nil)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})

	t.Run("GetStudySessions", func(t *testing.T) {
		helper, err := newTestHelper(t)
		require.NoError(t, err)

		handler := NewGroupHandler(helper.db)
		helper.router.GET("/api/groups/:id/study_sessions", handler.GetStudySessions)

		// Seed test data
		err = helper.seedTestData()
		require.NoError(t, err)

		// Test successful get study sessions request
		w := performRequest(helper.router, "GET", "/api/groups/1/study_sessions", nil)
		assert.Equal(t, http.StatusOK, w.Code)

		var sessions []map[string]interface{}
		err = json.Unmarshal(w.Body.Bytes(), &sessions)
		assert.NoError(t, err)
		assert.Len(t, sessions, 1)

		session := sessions[0]
		assert.NotNil(t, session["id"])
		assert.NotNil(t, session["completed_at"])
		assert.NotNil(t, session["activity"])
		assert.NotNil(t, session["stats"])

		stats := session["stats"].(map[string]interface{})
		assert.Equal(t, float64(1), stats["correct_count"])
		assert.Equal(t, float64(1), stats["wrong_count"])
		assert.Equal(t, float64(50), stats["success_rate"])

		// Test non-existent group
		w = performRequest(helper.router, "GET", "/api/groups/999/study_sessions", nil)
		assert.Equal(t, http.StatusInternalServerError, w.Code)

		// Test invalid ID format
		w = performRequest(helper.router, "GET", "/api/groups/invalid/study_sessions", nil)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})
}
