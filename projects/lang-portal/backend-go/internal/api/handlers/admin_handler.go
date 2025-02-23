package handlers

import (
	"fmt"
	"net/http"

	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/models"
	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/pkg/database"
	"github.com/gin-gonic/gin"
	"gorm.io/gorm"
)

// AdminHandler handles administrative functions
type AdminHandler struct {
	db *gorm.DB
}

// NewAdminHandler creates a new admin handler instance
func NewAdminHandler(db *gorm.DB) *AdminHandler {
	return &AdminHandler{db: db}
}

// ResetHistory resets user study history
func (h *AdminHandler) ResetHistory(c *gin.Context) {
	err := h.db.Transaction(func(tx *gorm.DB) error {
		// Reset study sessions
		if err := tx.Where("1 = 1").Delete(&models.StudySession{}).Error; err != nil {
			return fmt.Errorf("failed to delete study sessions: %v", err)
		}

		// Get all words
		var words []models.Word
		if err := tx.Find(&words).Error; err != nil {
			return fmt.Errorf("failed to fetch words: %v", err)
		}

		// Reset statistics for each word
		for _, word := range words {
			word.CorrectCount = 0
			word.WrongCount = 0
			if err := tx.Save(&word).Error; err != nil {
				return fmt.Errorf("failed to reset statistics for word %d: %v", word.ID, err)
			}
		}

		return nil
	})

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Study history reset successfully"})
}

// FullReset drops and reseeds all data
func (h *AdminHandler) FullReset(c *gin.Context) {
	if err := database.ResetDB(h.db); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	// In tests, this will use test data, in production it uses main data
	if err := database.SeedDB(h.db); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Database reset successful"})
}
