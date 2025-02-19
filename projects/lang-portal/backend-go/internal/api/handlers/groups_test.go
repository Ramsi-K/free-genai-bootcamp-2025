package handlers

import (
	"encoding/json"
	"fmt"
	"net/http"
	"testing"
	"time"

	"github.com/Ramsi-K/free-genai-bootcamp-2025/projects/lang-portal/backend-go/internal/models"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestGroupHandler(t *testing.T) {
	t.Run("List", func(t *testing.T) {
		helper, err := newTestHelper(t)
		require.NoError(t, err)

		// Seed test data
		err = helper.seedTestData()
		require.NoError(t, err)

		// Test successful list request
		w := performRequest(helper.router, "GET", "/api/groups", nil)
		assert.Equal(t, http.StatusOK, w.Code)

		var groups []models.Group
		err = json.Unmarshal(w.Body.Bytes(), &groups)
		assert.NoError(t, err)
		assert.NotEmpty(t, groups)

		// Verify basic group properties
		basicWordsGroup := findGroup(groups, "Basic Words")
		require.NotNil(t, basicWordsGroup)
		assert.Equal(t, 2, basicWordsGroup.WordsCount)
	})

	t.Run("Get", func(t *testing.T) {
		helper, err := newTestHelper(t)
		require.NoError(t, err)

		// Seed test data
		err = helper.seedTestData()
		require.NoError(t, err)

		// Get the first group's ID
		w := performRequest(helper.router, "GET", "/api/groups", nil)
		assert.Equal(t, http.StatusOK, w.Code)

		var groups []models.Group
		err = json.Unmarshal(w.Body.Bytes(), &groups)
		assert.NoError(t, err)
		assert.NotEmpty(t, groups)

		// Test successful get request
		w = performRequest(helper.router, "GET", fmt.Sprintf("/api/groups/%d", groups[0].ID), nil)
		assert.Equal(t, http.StatusOK, w.Code)

		var group models.Group
		err = json.Unmarshal(w.Body.Bytes(), &group)
		assert.NoError(t, err)
		assert.Equal(t, groups[0].Name, group.Name)

		// Test non-existent group
		w = performRequest(helper.router, "GET", "/api/groups/999", nil)
		assert.Equal(t, http.StatusNotFound, w.Code)

		// Test invalid ID format
		w = performRequest(helper.router, "GET", "/api/groups/invalid", nil)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})

	t.Run("Get Words in Group", func(t *testing.T) {
		helper, err := newTestHelper(t)
		require.NoError(t, err)

		// Seed test data
		err = helper.seedTestData()
		require.NoError(t, err)

		// Get Basic Words group ID
		w := performRequest(helper.router, "GET", "/api/groups", nil)
		assert.Equal(t, http.StatusOK, w.Code)

		var groups []models.Group
		err = json.Unmarshal(w.Body.Bytes(), &groups)
		assert.NoError(t, err)

		basicWordsGroup := findGroup(groups, "Basic Words")
		require.NotNil(t, basicWordsGroup)

		// Get words in Basic Words group
		w = performRequest(helper.router, "GET", fmt.Sprintf("/api/groups/%d/words", basicWordsGroup.ID), nil)
		assert.Equal(t, http.StatusOK, w.Code)

		var words []models.Word
		err = json.Unmarshal(w.Body.Bytes(), &words)
		assert.NoError(t, err)
		assert.Equal(t, 2, len(words))

		// Verify word properties
		for _, word := range words {
			assert.NotEmpty(t, word.Hangul)
			assert.NotEmpty(t, word.English)
			assert.Contains(t, []string{"학교", "사과"}, word.Hangul)
		}

		// Test non-existent group
		w = performRequest(helper.router, "GET", "/api/groups/999/words", nil)
		assert.Equal(t, http.StatusNotFound, w.Code)

		// Test invalid group ID
		w = performRequest(helper.router, "GET", "/api/groups/invalid/words", nil)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})

	t.Run("GetStudySessions", func(t *testing.T) {
		helper, err := newTestHelper(t)
		require.NoError(t, err)

		// Seed test data
		err = helper.seedTestData()
		require.NoError(t, err)

		// Get the first group's ID
		w := performRequest(helper.router, "GET", "/api/groups", nil)
		assert.Equal(t, http.StatusOK, w.Code)

		var groups []models.Group
		err = json.Unmarshal(w.Body.Bytes(), &groups)
		assert.NoError(t, err)
		assert.NotEmpty(t, groups)

		// Create a test study session
		now := time.Now()
		session := models.StudySession{
			GroupID:         groups[0].ID,
			StudyActivityID: 1,
			CompletedAt:     &now,
		}
		err = helper.db.Create(&session).Error
		require.NoError(t, err)

		// Create test reviews
		reviews := []models.WordReview{
			{
				StudySessionID: session.ID,
				WordID:         1,
				Correct:        true,
			},
			{
				StudySessionID: session.ID,
				WordID:         2,
				Correct:        false,
			},
		}
		err = helper.db.Create(&reviews).Error
		require.NoError(t, err)

		// Test successful get study sessions request
		w = performRequest(helper.router, "GET", fmt.Sprintf("/api/groups/%d/study_sessions", groups[0].ID), nil)
		assert.Equal(t, http.StatusOK, w.Code)

		var sessions []map[string]interface{}
		err = json.Unmarshal(w.Body.Bytes(), &sessions)
		assert.NoError(t, err)
		assert.NotEmpty(t, sessions)

		// Check if we have any sessions
		if len(sessions) > 0 {
			session := sessions[0]
			assert.NotNil(t, session["id"])
			assert.NotNil(t, session["completed_at"])
			assert.NotNil(t, session["activity"])
			assert.NotNil(t, session["stats"])

			stats := session["stats"].(map[string]interface{})
			assert.Equal(t, float64(1), stats["correct_count"])
			assert.Equal(t, float64(1), stats["wrong_count"])
			assert.Equal(t, float64(50), stats["success_rate"])
		}

		// Test non-existent group
		w = performRequest(helper.router, "GET", "/api/groups/999/study_sessions", nil)
		assert.Equal(t, http.StatusNotFound, w.Code)

		// Test invalid ID format
		w = performRequest(helper.router, "GET", "/api/groups/invalid/study_sessions", nil)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})
}

// Helper function to find a group by name
func findGroup(groups []models.Group, name string) *models.Group {
	for i := range groups {
		if groups[i].Name == name {
			return &groups[i]
		}
	}
	return nil
}
