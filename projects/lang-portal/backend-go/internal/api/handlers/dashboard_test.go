package handlers

import (
	"encoding/json"
	"net/http"
	"testing"
	"time"

	"github.com/Ramsi-K/free-genai-bootcamp-2025/tree/main/projects/lang-portal/backend-go/internal/models"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestDashboardHandler(t *testing.T) {
	t.Run("GetDashboard", func(t *testing.T) {
		helper, err := newTestHelper(t)
		require.NoError(t, err)

		// Seed test data
		err = helper.seedTestData()
		require.NoError(t, err)

		// Create a test study session
		now := time.Now()
		session := models.StudySession{
			GroupID:         1,
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

		w := performRequest(helper.router, "GET", "/api/dashboard", nil)
		assert.Equal(t, http.StatusOK, w.Code)

		var response models.DashboardData
		err = json.Unmarshal(w.Body.Bytes(), &response)
		require.NoError(t, err)

		// Verify last study session
		assert.NotNil(t, response.LastStudySession)
		assert.Equal(t, session.GroupID, response.LastStudySession.GroupID)
		assert.Equal(t, 1, response.LastStudySession.Stats.CorrectCount)
		assert.Equal(t, 1, response.LastStudySession.Stats.WrongCount)

		// Verify study progress
		assert.Equal(t, 2, response.StudyProgress.WordsStudied)
		assert.Equal(t, 2, response.StudyProgress.TotalWords)
		assert.Equal(t, float64(50), response.StudyProgress.MasteryProgress)

		// Verify quick stats
		assert.Equal(t, float64(50), response.QuickStats.SuccessRate)
		assert.Equal(t, 1, response.QuickStats.TotalSessions)
		assert.Equal(t, 1, response.QuickStats.TotalActiveGroups)
		assert.Equal(t, 1, response.QuickStats.StudyStreak)
	})
}
