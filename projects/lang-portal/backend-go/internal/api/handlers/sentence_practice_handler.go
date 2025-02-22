package handlers

import (
	"net/http"
	"strconv"
	"strings"
	"time"

	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/models"
	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/repository"
	"github.com/gin-gonic/gin"
	"gorm.io/gorm"
)

// SentencePracticeHandler handles sentence practice-related requests
type SentencePracticeHandler struct {
	wordRepo repository.WordRepository
	db       *gorm.DB
}

// NewSentencePracticeHandler creates a new sentence practice handler instance
func NewSentencePracticeHandler(wordRepo repository.WordRepository, db *gorm.DB) *SentencePracticeHandler {
	return &SentencePracticeHandler{wordRepo: wordRepo, db: db}
}

// PracticeSentenceResponse defines the structure for sentence practice response
type PracticeSentenceResponse struct {
	Word             string   `json:"word"`
	ExampleSentences []string `json:"example_sentences"`
}

// SentencePracticeRequest defines the structure for sentence practice request
type SentencePracticeRequest struct {
	WordID      uint   `json:"word_id" binding:"required"`
	UserAnswer  string `json:"user_answer" binding:"required"`
	CorrectText string `json:"correct_text"`
}

// SentencePracticeAttemptResponse defines the structure for practice attempt response
type SentencePracticeAttemptResponse struct {
	IsCorrect      bool    `json:"is_correct"`
	Score          float64 `json:"score"`
	CorrectAnswer  string  `json:"correct_answer"`
	FeedbackPoints []struct {
		Point     string `json:"point"`
		IsCorrect bool   `json:"is_correct"`
	} `json:"feedback_points,omitempty"`
}

// SentencePracticeStatistics defines the structure for practice statistics
type SentencePracticeStatistics struct {
	TotalAttempts   int     `json:"total_attempts"`
	CorrectAttempts int     `json:"correct_attempts"`
	SuccessRate     float64 `json:"success_rate"`
	AverageScore    float64 `json:"average_score"`
	RecentScores    []struct {
		Date  string  `json:"date"`
		Score float64 `json:"score"`
	} `json:"recent_scores"`
}

// GetSentencePractice returns a practice sentence for a given word
func (h *SentencePracticeHandler) GetSentencePractice(c *gin.Context) {
	// Get a random word with sentence
	var word models.Word
	result := h.db.Preload("Sentences").
		Joins("JOIN sentences ON sentences.word_id = words.id").
		Order("RANDOM()").
		First(&word)

	if result.Error != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "No practice sentences available"})
		return
	}

	// Make sure we have sentences
	if len(word.Sentences) == 0 {
		c.JSON(http.StatusNotFound, gin.H{"error": "No example sentences for this word"})
		return
	}

	// Select the first sentence (or pick a random one if you prefer)
	sentence := word.Sentences[0]

	response := PracticeSentenceResponse{
		Word:             word.Hangul,
		ExampleSentences: []string{sentence.Korean, sentence.English},
	}

	c.JSON(http.StatusOK, response)
}

// PostSentencePracticeAttempt handles the sentence practice attempt endpoint

func (h *SentencePracticeHandler) PostSentencePracticeAttempt(c *gin.Context) {
	var request SentencePracticeRequest
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request format"})
		return
	}

	// Get the word
	word, err := h.wordRepo.GetWord(request.WordID)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Word not found"})
		return
	}

	// Find the matching sentence (using trimmed values)
	var correctSentence string
	for _, sentence := range word.Sentences {
		if strings.TrimSpace(sentence.Korean) == strings.TrimSpace(request.CorrectText) ||
			strings.TrimSpace(sentence.English) == strings.TrimSpace(request.CorrectText) {
			correctSentence = request.CorrectText
			break
		}
	}

	if correctSentence == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Provided correct_text doesn't match any sentence for this word"})
		return
	}

	// Calculate similarity score
	isExactMatch := strings.TrimSpace(request.UserAnswer) == strings.TrimSpace(correctSentence)
	var score float64 = 0
	if isExactMatch {
		score = 100
	} else if len(request.UserAnswer) > 0 {
		score = float64(len(request.UserAnswer)) / float64(len(correctSentence)) * 80
		if score > 80 {
			score = 80
		}
	}

	isCorrect := score >= 80

	studySession := models.StudySession{
		StudyActivityID: 1, // Assuming 1 is your sentence practice activity ID
		CorrectCount:    0,
		WrongCount:      0,
		CompletedAt:     time.Now(),
	}
	if isCorrect {
		studySession.CorrectCount = 1
	} else {
		studySession.WrongCount = 1
	}

	if err := h.db.Create(&studySession).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to record attempt"})
		return
	}

	wordReview := models.WordReviewItem{
		WordID:         request.WordID,
		StudySessionID: studySession.ID,
		CorrectCount:   0,
		CreatedAt:      time.Now(),
	}
	if isCorrect {
		wordReview.CorrectCount = 1
	}

	if err := h.db.Create(&wordReview).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to record word review"})
		return
	}

	if isCorrect {
		h.db.Model(&word).Update("correct_count", gorm.Expr("correct_count + ?", 1))
	} else {
		h.db.Model(&word).Update("wrong_count", gorm.Expr("wrong_count + ?", 1))
	}

	response := SentencePracticeAttemptResponse{
		IsCorrect:     isCorrect,
		Score:         score,
		CorrectAnswer: correctSentence,
	}
	c.JSON(http.StatusOK, response)
}

// func (h *SentencePracticeHandler) PostSentencePracticeAttempt(c *gin.Context) {
// 	var request SentencePracticeRequest
// 	if err := c.ShouldBindJSON(&request); err != nil {
// 		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request format"})
// 		return
// 	}

// 	// Get the word
// 	word, err := h.wordRepo.GetWord(request.WordID)
// 	if err != nil {
// 		c.JSON(http.StatusNotFound, gin.H{"error": "Word not found"})
// 		return
// 	}

// 	// Find the matching sentence
// 	var correctSentence string
// 	for _, sentence := range word.Sentences {
// 		if sentence.Korean == request.CorrectText || sentence.English == request.CorrectText {
// 			correctSentence = request.CorrectText
// 			break
// 		}
// 	}

// 	if correctSentence == "" {
// 		c.JSON(http.StatusBadRequest, gin.H{"error": "Provided correct_text doesn't match any sentence for this word"})
// 		return
// 	}

// 	// Calculate similarity score (in a real app, you'd want a more sophisticated algorithm)
// 	// This is a simple placeholder
// 	isExactMatch := request.UserAnswer == correctSentence
// 	var score float64 = 0
// 	if isExactMatch {
// 		score = 100
// 	} else {
// 		// Calculate a similarity score
// 		// For a simple implementation, we'll just check if it contains the word
// 		if len(request.UserAnswer) > 0 && request.UserAnswer != "" {
// 			// Award a partial score based on length
// 			score = float64(len(request.UserAnswer)) / float64(len(correctSentence)) * 80
// 			if score > 80 {
// 				score = 80 // Cap partial matches at 80%
// 			}
// 		}
// 	}

// 	// Create study session record
// 	isCorrect := score >= 80 // Consider 80% or higher as correct

// 	// Create a study session
// 	studySession := models.StudySession{
// 		StudyActivityID: 1, // Assuming 1 is your sentence practice activity ID
// 		CorrectCount:    0,
// 		WrongCount:      0,
// 		CompletedAt:     time.Now(),
// 	}

// 	if isCorrect {
// 		studySession.CorrectCount = 1
// 	} else {
// 		studySession.WrongCount = 1
// 	}

// 	if err := h.db.Create(&studySession).Error; err != nil {
// 		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to record attempt"})
// 		return
// 	}

// 	// Create word review record
// 	wordReview := models.WordReviewItem{
// 		WordID:         request.WordID,
// 		StudySessionID: studySession.ID,
// 		CorrectCount:   0,
// 		CreatedAt:      time.Now(),
// 	}

// 	if isCorrect {
// 		wordReview.CorrectCount = 1
// 	}

// 	if err := h.db.Create(&wordReview).Error; err != nil {
// 		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to record word review"})
// 		return
// 	}

// 	// Update word stats
// 	if isCorrect {
// 		h.db.Model(&word).Update("correct_count", gorm.Expr("correct_count + ?", 1))
// 	} else {
// 		h.db.Model(&word).Update("wrong_count", gorm.Expr("wrong_count + ?", 1))
// 	}

// 	// Prepare response
// 	response := SentencePracticeAttemptResponse{
// 		IsCorrect:     isCorrect,
// 		Score:         score,
// 		CorrectAnswer: correctSentence,
// 	}

// 	c.JSON(http.StatusOK, response)
// }

// GetSentencePracticeStatistics handles the sentence practice statistics endpoint
func (h *SentencePracticeHandler) GetSentencePracticeStatistics(c *gin.Context) {
	// Get user ID if available (for future personalization)
	// userID := c.GetString("user_id") // In a real app with auth

	// Calculate overall statistics
	var totalAttempts, correctAttempts int64

	// Get total attempts from study sessions related to sentence practice
	h.db.Model(&models.StudySession{}).
		Where("study_activity_id = ?", 1). // Assuming ID 1 is sentence practice
		Count(&totalAttempts)

	// Get correct attempts
	h.db.Model(&models.StudySession{}).
		Where("study_activity_id = ? AND correct_count > 0", 1).
		Count(&correctAttempts)

	// Calculate success rate
	var successRate float64 = 0
	if totalAttempts > 0 {
		successRate = float64(correctAttempts) / float64(totalAttempts) * 100
	}

	// Get average score (in a real app, you'd store the actual score)
	// This is a simplified version
	var averageScore float64 = successRate

	// Create statistics response
	stats := SentencePracticeStatistics{
		TotalAttempts:   int(totalAttempts),
		CorrectAttempts: int(correctAttempts),
		SuccessRate:     successRate,
		AverageScore:    averageScore,
		RecentScores: make([]struct {
			Date  string  `json:"date"`
			Score float64 `json:"score"`
		}, 0),
	}

	// Get recent sessions for the graph data
	var recentSessions []models.StudySession
	h.db.Where("study_activity_id = ?", 1).
		Order("completed_at DESC").
		Limit(10).
		Find(&recentSessions)

	// Transform into scores for the graph
	for _, session := range recentSessions {
		// Calculate a score based on correct vs. wrong
		var sessionScore float64 = 0
		if session.CorrectCount+session.WrongCount > 0 {
			sessionScore = float64(session.CorrectCount) / float64(session.CorrectCount+session.WrongCount) * 100
		}

		// Format date
		dateStr := session.CompletedAt.Format("2006-01-02")

		// Add to recent scores
		stats.RecentScores = append(stats.RecentScores, struct {
			Date  string  `json:"date"`
			Score float64 `json:"score"`
		}{
			Date:  dateStr,
			Score: sessionScore,
		})
	}

	c.JSON(http.StatusOK, stats)
}

// GetSentencePracticeExamples returns example sentences for a given word
func (h *SentencePracticeHandler) GetSentencePracticeExamples(c *gin.Context) {
	wordIDStr := c.Query("word_id")
	if wordIDStr == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Word ID parameter is required"})
		return
	}

	wordID, err := strconv.Atoi(wordIDStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid word ID"})
		return
	}

	word, err := h.wordRepo.GetWord(uint(wordID))
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Word not found"})
		return
	}

	// Make sure we have sentences
	if len(word.Sentences) == 0 {
		c.JSON(http.StatusNotFound, gin.H{"error": "No example sentences for this word"})
		return
	}

	response := PracticeSentenceResponse{
		Word:             word.Hangul,
		ExampleSentences: []string{word.Sentences[0].Korean, word.Sentences[0].English},
	}

	c.JSON(http.StatusOK, response)
}
