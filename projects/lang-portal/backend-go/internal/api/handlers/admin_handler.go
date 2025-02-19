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
			word.StudyStatistics = models.StudyStatistics{
				CorrectCount: 0,
				WrongCount:   0,
			}
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
	// Drop all tables
	if err := h.db.Migrator().DropTable(
		&models.StudySession{},
		&models.WordReviewItem{},
		"group_words", // Drop join table first
		&models.Word{},
		&models.WordGroup{},
		&models.StudyActivity{},
	); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": fmt.Sprintf("failed to drop tables: %v", err)})
		return
	}

	// Run migrations
	if err := h.db.AutoMigrate(
		&models.Word{},
		&models.WordGroup{},
		&models.StudyActivity{},
		&models.StudySession{},
		&models.WordReviewItem{},
	); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": fmt.Sprintf("failed to run migrations: %v", err)})
		return
	}

	// Load seed data
	if err := database.SeedDB(h.db); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": fmt.Sprintf("failed to load seed data: %v", err)})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Database reset successfully"})
}
