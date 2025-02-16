package handlers

import (
	"net/http"

	"github.com/Ramsi-K/free-genai-bootcamp-2025/tree/main/projects/lang-portal/backend-go/internal/models"

	"github.com/gin-gonic/gin"
	"gorm.io/gorm"
)

type StudySessionHandler struct {
	db *gorm.DB
}

func NewStudySessionHandler(db *gorm.DB) *StudySessionHandler {
	return &StudySessionHandler{db: db}
}

func (h *StudySessionHandler) Create(c *gin.Context) {
	var input struct {
		GroupID uint `json:"group_id" binding:"required"`
	}

	if err := c.ShouldBindJSON(&input); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Verify group exists
	var group models.Group
	if err := h.db.First(&group, input.GroupID).Error; err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid group_id"})
		return
	}

	session := models.StudySession{
		GroupID: input.GroupID,
	}

	if err := h.db.Create(&session).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create study session"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"id":       session.ID,
		"group_id": session.GroupID,
	})
}
