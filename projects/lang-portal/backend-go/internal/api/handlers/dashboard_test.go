package handlers

import (
	"encoding/json"
	"net/http"
	"testing"

	"github.com/Ramsi-K/free-genai-bootcamp-2025/tree/main/projects/lang-portal/backend-go/internal/models"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestDashboardHandler(t *testing.T) {
	t.Run("GetDashboard", func(t *testing.T) {
		helper, err := newTestHelper(t)
		require.NoError(t, err)

		handler := NewDashboardHandler(helper.db)
		helper.router.GET("/api/dashboard", handler.GetDashboard)

		// Test empty database
		w := performRequest(helper.router, "GET", "/api/dashboard", nil)
		assert.Equal(t, http.StatusOK, w.Code)

		var emptyData models.DashboardData
		err = json.Unmarshal(w.Body.Bytes(), &emptyData)
		assert.NoError(t, err)
		assert.Nil(t, emptyData.LastStudySession)
		assert.Equal(t, 0, emptyData.StudyProgress.WordsStudied)
		assert.Equal(t, 0, emptyData.StudyProgress.TotalWords)
		assert.Equal(t, float64(0), emptyData.StudyProgress.MasteryProgress)
		assert.Equal(t, float64(0), emptyData.QuickStats.SuccessRate)
		assert.Equal(t, 0, emptyData.QuickStats.TotalSessions)
		assert.Equal(t, 0, emptyData.QuickStats.TotalActiveGroups)
		assert.Equal(t, 0, emptyData.QuickStats.StudyStreak)

		// Seed test data
		err = helper.seedTestData()
		require.NoError(t, err)

		// Test with data
		w = performRequest(helper.router, "GET", "/api/dashboard", nil)
		assert.Equal(t, http.StatusOK, w.Code)

		var dashboardData models.DashboardData
		err = json.Unmarshal(w.Body.Bytes(), &dashboardData)
		assert.NoError(t, err)

		// Test last study session
		assert.NotNil(t, dashboardData.LastStudySession)
		assert.Equal(t, "Flashcards", dashboardData.LastStudySession.ActivityName)
		assert.Equal(t, "School-related Words", dashboardData.LastStudySession.GroupName)
		assert.Equal(t, uint(1), dashboardData.LastStudySession.GroupID)
		assert.Equal(t, 1, dashboardData.LastStudySession.Stats.CorrectCount)
		assert.Equal(t, 1, dashboardData.LastStudySession.Stats.WrongCount)

		// Test study progress
		assert.Equal(t, 2, dashboardData.StudyProgress.WordsStudied)
		assert.Equal(t, 2, dashboardData.StudyProgress.TotalWords)
		assert.Equal(t, float64(50), dashboardData.StudyProgress.MasteryProgress)

		// Test quick stats
		assert.Equal(t, float64(50), dashboardData.QuickStats.SuccessRate)
		assert.Equal(t, 1, dashboardData.QuickStats.TotalSessions)
		assert.Equal(t, 1, dashboardData.QuickStats.TotalActiveGroups)
		assert.Equal(t, 1, dashboardData.QuickStats.StudyStreak)
	})
}
