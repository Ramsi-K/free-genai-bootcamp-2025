package handlers

import (
	"net/http"

	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/models"
	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/pkg/database"
	"github.com/gin-gonic/gin"
)

// AdminHandler handles administrative functions
type AdminHandler struct{}

// NewAdminHandler creates a new admin handler instance
func NewAdminHandler() *AdminHandler {
	return &AdminHandler{}
}

// ResetHistory resets user study history
func (h *AdminHandler) ResetHistory(c *gin.Context) {
	db := database.GetDB()

	// Reset study sessions
	if err := db.Exec("DELETE FROM study_sessions").Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error resetting study history"})
		return
	}

	// Reset word statistics
	if err := db.Model(&models.Word{}).Updates(map[string]interface{}{
		"study_statistics": struct {
			CorrectCount int `json:"correct_count"`
			WrongCount   int `json:"wrong_count"`
		}{
			CorrectCount: 0,
			WrongCount:   0,
		},
	}).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error resetting word statistics"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Study history reset successfully"})
}

// FullReset drops and reseeds all data
func (h *AdminHandler) FullReset(c *gin.Context) {
	db := database.GetDB()

	// Drop all tables
	if err := db.Exec("DROP TABLE IF EXISTS study_sessions, group_words, words, word_groups, study_activities").Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error dropping tables"})
		return
	}

	// Run migrations
	if err := database.Initialize(); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error initializing database"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Database reset and reseeded successfully"})
}
