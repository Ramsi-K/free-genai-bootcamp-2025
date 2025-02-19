package handlers

import (
	"net/http"
	"time"

	"github.com/Ramsi-K/free-genai-bootcamp-2025/tree/main/projects/lang-portal/backend-go/internal/models"
	"github.com/gin-gonic/gin"
	"gorm.io/gorm"
)

type DashboardHandler struct {
	db *gorm.DB
}

func NewDashboardHandler(db *gorm.DB) *DashboardHandler {
	return &DashboardHandler{db: db}
}

func (h *DashboardHandler) GetDashboard(c *gin.Context) {
	dashboardData := &models.DashboardData{}

	// Get last study session
	var lastSession models.StudySession
	if err := h.db.Where("completed_at IS NOT NULL").
		Preload("Activity").
		Preload("Group").
		Preload("Reviews").
		Order("completed_at DESC").
		First(&lastSession).Error; err != nil && err != gorm.ErrRecordNotFound {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error fetching last session"})
		return
	}

	if lastSession.ID != 0 {
		stats := lastSession.GetStats()
		dashboardData.LastStudySession = &models.LastStudySession{
			ActivityName: lastSession.Activity.Name,
			GroupName:    lastSession.Group.Name,
			Timestamp:    *lastSession.CompletedAt,
			Stats: struct {
				CorrectCount int `json:"correct_count"`
				WrongCount   int `json:"wrong_count"`
			}{
				CorrectCount: stats["correct_count"].(int),
				WrongCount:   stats["wrong_count"].(int),
			},
			GroupID: lastSession.GroupID,
		}
	}

	// Get study progress
	var totalWords int64
	h.db.Model(&models.Word{}).Where("deleted_at IS NULL").Count(&totalWords)

	var studiedWords int64
	h.db.Model(&models.WordReview{}).Where("deleted_at IS NULL").Distinct("word_id").Count(&studiedWords)

	var totalCorrect int64
	h.db.Model(&models.WordReview{}).Where("correct = ? AND deleted_at IS NULL", true).Count(&totalCorrect)

	var totalReviews int64
	h.db.Model(&models.WordReview{}).Where("deleted_at IS NULL").Count(&totalReviews)

	var masteryProgress float64
	if totalReviews > 0 {
		masteryProgress = float64(totalCorrect) / float64(totalReviews) * 100
	}

	dashboardData.StudyProgress = models.StudyProgress{
		WordsStudied:    int(studiedWords),
		TotalWords:      int(totalWords),
		MasteryProgress: masteryProgress,
	}

	// Get quick stats
	var totalSessions int64
	h.db.Model(&models.StudySession{}).Where("deleted_at IS NULL").Count(&totalSessions)

	var activeGroups int64
	h.db.Model(&models.Group{}).Where("words_count > 0 AND deleted_at IS NULL").Count(&activeGroups)

	// Calculate study streak
	streak := h.calculateStudyStreak()

	var successRate float64
	if totalReviews > 0 {
		successRate = float64(totalCorrect) / float64(totalReviews) * 100
	}

	dashboardData.QuickStats = models.QuickStats{
		SuccessRate:       successRate,
		TotalSessions:     int(totalSessions),
		TotalActiveGroups: int(activeGroups),
		StudyStreak:       streak,
	}

	// For example, count valid study sessions
	var sessionCount int64
	if err := h.db.Model(&models.StudySession{}).
		Where("completed_at IS NOT NULL AND deleted_at IS NULL").
		Count(&sessionCount).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error fetching dashboard data"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"completed_sessions": sessionCount,
		// ... include other dashboard fields as needed
	})
}

func (h *DashboardHandler) GetLastStudySession(c *gin.Context) {
	var lastSession models.StudySession
	if err := h.db.Preload("Activity").Preload("Group").Preload("Reviews").
		Order("completed_at DESC").First(&lastSession).Error; err != nil && err != gorm.ErrRecordNotFound {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error fetching last session"})
		return
	}

	if lastSession.ID == 0 {
		c.JSON(http.StatusOK, nil)
		return
	}

	stats := lastSession.GetStats()
	response := gin.H{
		"activity_name": lastSession.Activity.Name,
		"group_name":    lastSession.Group.Name,
		"timestamp":     lastSession.CompletedAt,
		"stats": gin.H{
			"correct_count": stats["correct_count"],
			"wrong_count":   stats["wrong_count"],
		},
		"group_id": lastSession.GroupID,
	}

	c.JSON(http.StatusOK, response)
}

func (h *DashboardHandler) GetStudyProgress(c *gin.Context) {
	var totalWords int64
	h.db.Model(&models.Word{}).Count(&totalWords)

	var studiedWords int64
	h.db.Model(&models.WordReview{}).Distinct("word_id").Count(&studiedWords)

	var totalCorrect int64
	h.db.Model(&models.WordReview{}).Where("correct = ?", true).Count(&totalCorrect)

	var totalReviews int64
	h.db.Model(&models.WordReview{}).Count(&totalReviews)

	var masteryProgress float64
	if totalReviews > 0 {
		masteryProgress = float64(totalCorrect) / float64(totalReviews) * 100
	}

	c.JSON(http.StatusOK, gin.H{
		"words_studied":    studiedWords,
		"total_words":      totalWords,
		"mastery_progress": masteryProgress,
	})
}

func (h *DashboardHandler) GetQuickStats(c *gin.Context) {
	var totalCorrect, totalReviews int64
	h.db.Model(&models.WordReview{}).Where("correct = ?", true).Count(&totalCorrect)
	h.db.Model(&models.WordReview{}).Count(&totalReviews)

	var successRate float64
	if totalReviews > 0 {
		successRate = float64(totalCorrect) / float64(totalReviews) * 100
	}

	var totalSessions int64
	h.db.Model(&models.StudySession{}).Count(&totalSessions)

	var activeGroups int64
	h.db.Model(&models.Group{}).Where("words_count > 0").Count(&activeGroups)

	streak := h.calculateStudyStreak()

	c.JSON(http.StatusOK, gin.H{
		"success_rate":        successRate,
		"total_sessions":      totalSessions,
		"total_active_groups": activeGroups,
		"study_streak":        streak,
	})
}

func (h *DashboardHandler) calculateStudyStreak() int {
	var sessions []models.StudySession
	if err := h.db.Where("completed_at IS NOT NULL AND deleted_at IS NULL").
		Order("completed_at DESC").
		Find(&sessions).Error; err != nil {
		return 0
	}

	if len(sessions) == 0 {
		return 0
	}

	streak := 1
	currentDate := sessions[0].CompletedAt.Truncate(24 * time.Hour)
	previousDate := currentDate.Add(-24 * time.Hour)

	for i := 1; i < len(sessions); i++ {
		sessionDate := sessions[i].CompletedAt.Truncate(24 * time.Hour)
		if sessionDate.Equal(previousDate) {
			previousDate = previousDate.Add(-24 * time.Hour)
			streak++
		} else if sessionDate.Before(previousDate) {
			break
		}
	}

	return streak
}
