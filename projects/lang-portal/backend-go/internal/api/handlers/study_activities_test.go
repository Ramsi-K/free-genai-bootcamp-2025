package handlers

import (
	"encoding/json"
	"net/http"
	"testing"

	"github.com/Ramsi-K/free-genai-bootcamp-2025/tree/main/projects/lang-portal/backend-go/internal/models"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestStudyActivityHandler(t *testing.T) {
	t.Run("List", func(t *testing.T) {
		helper, err := newTestHelper(t)
		require.NoError(t, err)

		handler := NewStudyActivityHandler(helper.db)
		helper.router.GET("/api/study_activities", handler.List)

		// Seed test data
		err = helper.seedTestData()
		require.NoError(t, err)

		// Test successful list request
		w := performRequest(helper.router, "GET", "/api/study_activities", nil)
		assert.Equal(t, http.StatusOK, w.Code)

		var activities []models.StudyActivity
		err = json.Unmarshal(w.Body.Bytes(), &activities)
		assert.NoError(t, err)
		assert.Len(t, activities, 2)
		assert.Equal(t, "Flashcards", activities[0].Name)
		assert.Equal(t, "flashcards", activities[0].Type)
	})

	t.Run("Get", func(t *testing.T) {
		helper, err := newTestHelper(t)
		require.NoError(t, err)

		handler := NewStudyActivityHandler(helper.db)
		helper.router.GET("/api/study_activities/:id", handler.Get)

		// Seed test data
		err = helper.seedTestData()
		require.NoError(t, err)

		// Test successful get request
		w := performRequest(helper.router, "GET", "/api/study_activities/1", nil)
		assert.Equal(t, http.StatusOK, w.Code)

		var activity models.StudyActivity
		err = json.Unmarshal(w.Body.Bytes(), &activity)
		assert.NoError(t, err)
		assert.Equal(t, "Flashcards", activity.Name)
		assert.Equal(t, "flashcards", activity.Type)

		// Test non-existent activity
		w = performRequest(helper.router, "GET", "/api/study_activities/999", nil)
		assert.Equal(t, http.StatusNotFound, w.Code)

		// Test invalid ID format
		w = performRequest(helper.router, "GET", "/api/study_activities/invalid", nil)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})

	t.Run("GetSessions", func(t *testing.T) {
		helper, err := newTestHelper(t)
		require.NoError(t, err)

		handler := NewStudyActivityHandler(helper.db)
		helper.router.GET("/api/study_activities/:id/study_sessions", handler.GetSessions)

		// Seed test data
		err = helper.seedTestData()
		require.NoError(t, err)

		// Test successful get sessions request
		w := performRequest(helper.router, "GET", "/api/study_activities/1/study_sessions", nil)
		assert.Equal(t, http.StatusOK, w.Code)

		var sessions []map[string]interface{}
		err = json.Unmarshal(w.Body.Bytes(), &sessions)
		assert.NoError(t, err)
		assert.Len(t, sessions, 1)

		session := sessions[0]
		assert.NotNil(t, session["id"])
		assert.NotNil(t, session["completed_at"])
		assert.NotNil(t, session["group"])
		assert.NotNil(t, session["stats"])

		stats := session["stats"].(map[string]interface{})
		assert.Equal(t, float64(1), stats["correct_count"])
		assert.Equal(t, float64(1), stats["wrong_count"])
		assert.Equal(t, float64(50), stats["success_rate"])

		// Test non-existent activity
		w = performRequest(helper.router, "GET", "/api/study_activities/999/study_sessions", nil)
		assert.Equal(t, http.StatusOK, w.Code) // Returns empty array
		err = json.Unmarshal(w.Body.Bytes(), &sessions)
		assert.NoError(t, err)
		assert.Len(t, sessions, 0)

		// Test invalid ID format
		w = performRequest(helper.router, "GET", "/api/study_activities/invalid/study_sessions", nil)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})

	t.Run("Launch", func(t *testing.T) {
		helper, err := newTestHelper(t)
		require.NoError(t, err)

		handler := NewStudyActivityHandler(helper.db)
		helper.router.POST("/api/study_activities/:id/launch", handler.Launch)

		// Seed test data
		err = helper.seedTestData()
		require.NoError(t, err)

		// Test successful launch request
		w := performRequest(helper.router, "POST", "/api/study_activities/1/launch", map[string]interface{}{
			"group_id": 1,
		})
		assert.Equal(t, http.StatusCreated, w.Code)

		var session models.StudySession
		err = json.Unmarshal(w.Body.Bytes(), &session)
		assert.NoError(t, err)
		assert.Equal(t, uint(1), session.GroupID)
		assert.Equal(t, uint(1), session.StudyActivityID)

		// Test non-existent group
		w = performRequest(helper.router, "POST", "/api/study_activities/1/launch", map[string]interface{}{
			"group_id": 999,
		})
		assert.Equal(t, http.StatusNotFound, w.Code)

		// Test invalid activity ID
		w = performRequest(helper.router, "POST", "/api/study_activities/invalid/launch", map[string]interface{}{
			"group_id": 1,
		})
		assert.Equal(t, http.StatusBadRequest, w.Code)

		// Test missing group_id
		w = performRequest(helper.router, "POST", "/api/study_activities/1/launch", map[string]interface{}{})
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})
}
