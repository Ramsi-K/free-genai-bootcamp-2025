package handlers

import (
	"net/http"
	"net/http/httptest"
	"os"
	"testing"

	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/models"
	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
)

func TestAdminHandler_Integration(t *testing.T) {
	// Setup test environment
	os.Setenv("GO_ENV", "test")
	gin.SetMode(gin.TestMode)

	// Setup
	db, err := setupTestDB(t)
	assert.NoError(t, err)
	defer cleanupTestDB(db)

	// Setup router
	router := gin.New()
	handler := NewAdminHandler(db)
	router.POST("/api/admin/reset", handler.FullReset)

	t.Run("Full Reset", func(t *testing.T) {
		// Make request to reset endpoint
		req := httptest.NewRequest("POST", "/api/admin/reset", nil)
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)

		// Verify response
		assert.Equal(t, http.StatusOK, w.Code)

		// Verify database was reset with test data
		var wordCount int64
		db.Model(&models.Word{}).Count(&wordCount)
		assert.Greater(t, wordCount, int64(0), "Should have test words after reset")

		var groupCount int64
		db.Model(&models.WordGroup{}).Count(&groupCount)
		assert.Greater(t, groupCount, int64(0), "Should have test groups after reset")
	})
}
