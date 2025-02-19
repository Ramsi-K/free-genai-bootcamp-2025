package handlers

import (
	"net/http"
	"strconv"
	"time"

	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/models"
	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/repository"
	"github.com/gin-gonic/gin"
)

// StudyActivityHandler handles study activity-related requests
type StudyActivityHandler struct {
	activityRepo *repository.StudyActivityRepository
}

// NewStudyActivityHandler creates a new study activity handler instance
func NewStudyActivityHandler(repo *repository.StudyActivityRepository) *StudyActivityHandler {
	return &StudyActivityHandler{activityRepo: repo}
}

// ListActivities returns all study activities
func (h *StudyActivityHandler) ListActivities(c *gin.Context) {
	activities, err := h.activityRepo.ListActivities()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error fetching activities"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"data": activities})
}

// GetActivity returns details of a specific activity
func (h *StudyActivityHandler) GetActivity(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid activity ID"})
		return
	}

	activity, err := h.activityRepo.GetActivity(uint(id))
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Activity not found"})
		return
	}

	c.JSON(http.StatusOK, activity)
}

// CreateStudySession creates a new study session
func (h *StudyActivityHandler) CreateStudySession(c *gin.Context) {
	var session models.StudySession
	if err := c.ShouldBindJSON(&session); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request body"})
		return
	}

	session.CompletedAt = time.Now()
	if err := h.activityRepo.CreateStudySession(&session); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error creating study session"})
		return
	}

	c.JSON(http.StatusCreated, session)
}

// GetLastStudySession returns the most recent study session
func (h *StudyActivityHandler) GetLastStudySession(c *gin.Context) {
	session, err := h.activityRepo.GetLastStudySession()
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "No study sessions found"})
		return
	}

	c.JSON(http.StatusOK, session)
}

// GetStudyProgress returns overall study progress
func (h *StudyActivityHandler) GetStudyProgress(c *gin.Context) {
	progress, err := h.activityRepo.GetStudyProgress()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error fetching study progress"})
		return
	}

	c.JSON(http.StatusOK, progress)
}

// GetQuickStats returns quick learning statistics
func (h *StudyActivityHandler) GetQuickStats(c *gin.Context) {
	stats, err := h.activityRepo.GetQuickStats()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error fetching quick stats"})
		return
	}

	c.JSON(http.StatusOK, stats)
}
