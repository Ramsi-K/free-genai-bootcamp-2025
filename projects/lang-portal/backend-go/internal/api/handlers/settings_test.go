package handlers

import (
	"net/http"
	"testing"

	"github.com/Ramsi-K/free-genai-bootcamp-2025/tree/main/projects/lang-portal/backend-go/internal/models"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestSettingsHandler(t *testing.T) {
	t.Run("ResetHistory", func(t *testing.T) {
		helper, err := newTestHelper(t)
		require.NoError(t, err)

		handler := NewSettingsHandler(helper.db)
		helper.router.POST("/api/settings/reset_history", handler.ResetHistory)

		// Seed test data
		err = helper.seedTestData()
		require.NoError(t, err)

		// Verify initial data exists
		var sessionCount, reviewCount int64
		helper.db.Model(&models.StudySession{}).Count(&sessionCount)
		helper.db.Model(&models.WordReview{}).Count(&reviewCount)
		assert.Equal(t, int64(1), sessionCount)
		assert.Equal(t, int64(2), reviewCount)

		// Test reset history
		w := performRequest(helper.router, "POST", "/api/settings/reset_history", nil)
		assert.Equal(t, http.StatusOK, w.Code)

		// Verify data was deleted
		helper.db.Model(&models.StudySession{}).Count(&sessionCount)
		helper.db.Model(&models.WordReview{}).Count(&reviewCount)
		assert.Equal(t, int64(0), sessionCount)
		assert.Equal(t, int64(0), reviewCount)

		// Verify other data remains
		var wordCount, groupCount int64
		helper.db.Model(&models.Word{}).Count(&wordCount)
		helper.db.Model(&models.Group{}).Count(&groupCount)
		assert.Equal(t, int64(2), wordCount)
		assert.Equal(t, int64(2), groupCount)
	})

	t.Run("FullReset", func(t *testing.T) {
		helper, err := newTestHelper(t)
		require.NoError(t, err)

		handler := NewSettingsHandler(helper.db)
		helper.router.POST("/api/settings/full_reset", handler.FullReset)

		// Seed test data
		err = helper.seedTestData()
		require.NoError(t, err)

		// Verify initial data exists
		var wordCount, groupCount, sessionCount, reviewCount, activityCount int64
		helper.db.Model(&models.Word{}).Count(&wordCount)
		helper.db.Model(&models.Group{}).Count(&groupCount)
		helper.db.Model(&models.StudySession{}).Count(&sessionCount)
		helper.db.Model(&models.WordReview{}).Count(&reviewCount)
		helper.db.Model(&models.StudyActivity{}).Count(&activityCount)
		assert.Equal(t, int64(2), wordCount)
		assert.Equal(t, int64(2), groupCount)
		assert.Equal(t, int64(1), sessionCount)
		assert.Equal(t, int64(2), reviewCount)
		assert.Equal(t, int64(2), activityCount)

		// Test full reset
		w := performRequest(helper.router, "POST", "/api/settings/full_reset", nil)
		assert.Equal(t, http.StatusOK, w.Code)

		// Verify all data was deleted and tables recreated
		helper.db.Model(&models.Word{}).Count(&wordCount)
		helper.db.Model(&models.Group{}).Count(&groupCount)
		helper.db.Model(&models.StudySession{}).Count(&sessionCount)
		helper.db.Model(&models.WordReview{}).Count(&reviewCount)
		helper.db.Model(&models.StudyActivity{}).Count(&activityCount)
		assert.Equal(t, int64(0), wordCount)
		assert.Equal(t, int64(0), groupCount)
		assert.Equal(t, int64(0), sessionCount)
		assert.Equal(t, int64(0), reviewCount)
		assert.Equal(t, int64(3), activityCount) // Default activities from seed
	})
}
