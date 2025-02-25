package handlers

import (
	"encoding/json"
	"net/http"
	"testing"

	"github.com/Ramsi-K/free-genai-bootcamp-2025/projects/lang-portal/backend-go/internal/models"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestStudySessionHandler(t *testing.T) {
	t.Run("Create", func(t *testing.T) {
		// Setup
		helper, err := newTestHelper(t)
		require.NoError(t, err)

		// Seed test data
		err = helper.seedTestData()
		require.NoError(t, err)

		// Create request
		payload := map[string]interface{}{
			"group_id":          1,
			"study_activity_id": 1,
		}
		w := performRequest(helper.router, "POST", "/api/study_sessions", payload)

		// Assert response
		assert.Equal(t, http.StatusCreated, w.Code)

		var response models.StudySession
		err = json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)
		assert.Equal(t, uint(1), response.GroupID)
		assert.Equal(t, uint(1), response.StudyActivityID)
		assert.Nil(t, response.CompletedAt)
	})
}
