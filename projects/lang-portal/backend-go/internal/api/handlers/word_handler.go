package handlers

import (
	"log"
	"net/http"
	"strconv"
	"time"

	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/models" // Replace with your actual import path

	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/repository"
	"github.com/gin-gonic/gin"
)

// WordHandler handles word-related requests
type WordHandler struct {
	wordRepo repository.WordRepository
}

// NewWordHandler creates a new WordHandler instance
func NewWordHandler(repo repository.WordRepository) *WordHandler {
	return &WordHandler{wordRepo: repo}
}

func (h *WordHandler) ListWords(c *gin.Context) {
	pageStr := c.DefaultQuery("page", "1")
	limitStr := c.DefaultQuery("limit", "10")

	page, err := strconv.Atoi(pageStr)
	if err != nil || page <= 0 {
		log.Printf("Invalid page parameter: %s", pageStr)
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid page parameter"})
		return
	}

	limit, err := strconv.Atoi(limitStr)
	if err != nil || limit <= 0 {
		log.Printf("Invalid limit parameter: %s", limitStr)
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid limit parameter"})
		return
	}

	words, total, err := h.wordRepo.ListWords(page, limit)
	if err != nil {
		log.Printf("Error fetching words: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error fetching words"})
		return
	}

	log.Printf("Retrieved %d words out of %d total", len(words), total)

	c.JSON(http.StatusOK, gin.H{
		"data": words,
		"meta": gin.H{
			"current_page": page,
			"per_page":     limit,
			"total":        total,
		},
	})
}

// GetWord returns details of a specific word
func (h *WordHandler) GetWord(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid word ID"})
		return
	}

	word, err := h.wordRepo.GetWord(uint(id))
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Word not found"})
		return
	}

	c.JSON(http.StatusOK, word)
}

func (h *WordHandler) CreateCorrectStudySession(c *gin.Context) {
	id := c.Param("id")
	wordID, err := strconv.Atoi(id)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid word ID"})
		return
	}

	var word models.Word
	if err := h.wordRepo.GetDB().First(&word, wordID).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Word not found"})
		return
	}

	// Assuming you have a way to determine the ActivityID (e.g., from the request body)
	// For now, let's hardcode it or get it from a query parameter
	activityIDStr := c.DefaultQuery("activity_id", "1") // Default to activity ID 1
	activityID, err := strconv.Atoi(activityIDStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid activity ID"})
		return
	}

	studySession := models.StudySession{
		StudyActivityID: uint(activityID),
		CorrectCount:    0,
		WrongCount:      0,
	}

	if err := h.wordRepo.GetDB().Create(&studySession).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create study session"})
		return
	}

	wordReviewItem := models.WordReviewItem{
		WordID:         uint(wordID),
		StudySessionID: studySession.ID,
		CorrectCount:   1,
		CreatedAt:      time.Now(),
	}

	if err := h.wordRepo.GetDB().Create(&wordReviewItem).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create word review item"})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"message": "Study session created"})
}

// CreateIncorrectStudySession creates a new study session record for an incorrect attempt
func (h *WordHandler) CreateIncorrectStudySession(c *gin.Context) {
	id := c.Param("id")
	wordID, err := strconv.Atoi(id)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid word ID"})
		return
	}

	var word models.Word
	if err := h.wordRepo.GetDB().First(&word, wordID).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Word not found"})
		return
	}

	// Assuming you have a way to determine the ActivityID (e.g., from the request body)
	// For now, let's hardcode it or get it from a query parameter
	activityIDStr := c.DefaultQuery("activity_id", "1") // Default to activity ID 1
	activityID, err := strconv.Atoi(activityIDStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid activity ID"})
		return
	}

	studySession := models.StudySession{
		StudyActivityID: uint(activityID),
		CompletedAt:     time.Now(),
		CorrectCount:    0,
		WrongCount:      0,
	}

	if err := h.wordRepo.GetDB().Create(&studySession).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create study session"})
		return
	}

	wordReviewItem := models.WordReviewItem{
		WordID:         uint(wordID),
		StudySessionID: studySession.ID,
		CorrectCount:   0,
		CreatedAt:      time.Now(),
	}

	if err := h.wordRepo.GetDB().Create(&wordReviewItem).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create word review item"})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"message": "Study session created"})
}

func (h *WordHandler) GetStudyStatistics(wordID uint) (int, int, error) {
	var correctCount int64
	var wrongCount int64

	if err := h.wordRepo.GetDB().Model(&models.StudySession{}).Where("word_id = ? AND correct = ?", wordID, true).Count(&correctCount).Error; err != nil {
		return 0, 0, err
	}

	if err := h.wordRepo.GetDB().Model(&models.StudySession{}).Where("word_id = ? AND correct = ?", wordID, false).Count(&wrongCount).Error; err != nil {
		return 0, 0, err
	}

	return int(correctCount), int(wrongCount), nil
}
