package handlers

import (
	"net/http"
	"strconv"

	"github.com/Ramsi-K/free-genai-bootcamp-2025/tree/main/projects/lang-portal/backend-go/internal/models"
	"github.com/gin-gonic/gin"
	"gorm.io/gorm"
)

type StudyActivityHandler struct {
	db *gorm.DB
}

func NewStudyActivityHandler(db *gorm.DB) *StudyActivityHandler {
	return &StudyActivityHandler{db: db}
}

func (h *StudyActivityHandler) List(c *gin.Context) {
	var activities []models.StudyActivity
	if err := h.db.Find(&activities).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error fetching study activities"})
		return
	}

	c.JSON(http.StatusOK, activities)
}

func (h *StudyActivityHandler) Get(c *gin.Context) {
	id := c.Param("id")

	// Validate ID is numeric
	if _, err := strconv.ParseUint(id, 10, 64); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid ID format"})
		return
	}

	var activity models.StudyActivity
	if err := h.db.First(&activity, id).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			c.JSON(http.StatusNotFound, gin.H{"error": "Study activity not found"})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error fetching study activity"})
		return
	}

	c.JSON(http.StatusOK, activity)
}

func (h *StudyActivityHandler) GetSessions(c *gin.Context) {
	id := c.Param("id")

	// Validate ID is numeric
	if _, err := strconv.ParseUint(id, 10, 64); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid ID format"})
		return
	}

	var sessions []models.StudySession
	if err := h.db.Where("study_activity_id = ?", id).
		Preload("Group").
		Preload("Reviews").
		Order("completed_at DESC").
		Find(&sessions).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error fetching study sessions"})
		return
	}

	// Format response with statistics
	response := make([]gin.H, len(sessions))
	for i, session := range sessions {
		stats := session.GetStats()
		response[i] = gin.H{
			"id":           session.ID,
			"completed_at": session.CompletedAt,
			"group": gin.H{
				"id":   session.Group.ID,
				"name": session.Group.Name,
			},
			"stats": stats,
		}
	}

	c.JSON(http.StatusOK, response)
}

func (h *StudyActivityHandler) Launch(c *gin.Context) {
	id := c.Param("id")
	activityID, err := strconv.ParseUint(id, 10, 64)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid activity ID format"})
		return
	}

	var req struct {
		GroupID uint `json:"group_id" binding:"required"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request body"})
		return
	}

	// Verify group exists
	var group models.Group
	if err := h.db.First(&group, req.GroupID).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			c.JSON(http.StatusNotFound, gin.H{"error": "Group not found"})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error fetching group"})
		return
	}

	// Create new study session
	session := models.StudySession{
		GroupID:         req.GroupID,
		StudyActivityID: uint(activityID),
	}

	if err := h.db.Create(&session).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error creating study session"})
		return
	}

	c.JSON(http.StatusCreated, session)
}
