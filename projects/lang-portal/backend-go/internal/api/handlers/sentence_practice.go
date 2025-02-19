package handlers

import (
	"net/http"

	"github.com/Ramsi-K/free-genai-bootcamp-2025/tree/main/projects/lang-portal/backend-go/internal/models"
	"github.com/gin-gonic/gin"
	"gorm.io/gorm"
)

type SentencePracticeHandler struct {
	db *gorm.DB
}

func NewSentencePracticeHandler(db *gorm.DB) *SentencePracticeHandler {
	return &SentencePracticeHandler{db: db}
}

// GetPracticeSentence returns a random sentence for practice from data_korean.json
func (h *SentencePracticeHandler) GetPracticeSentence(c *gin.Context) {
	var word models.Word
	if err := h.db.Order("RANDOM()").
		Where("example_sentence IS NOT NULL").
		First(&word).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error fetching practice sentence"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"sentence_id": word.ID,
		"word": gin.H{
			"hangul":       word.Hangul,
			"romanization": word.Romanization,
			"english":      word.English,
		},
		"example_sentence": word.ExampleSentence,
	})
}

// SubmitSentenceAttempt handles user's attempt at translating a sentence
func (h *SentencePracticeHandler) SubmitSentenceAttempt(c *gin.Context) {
	var input struct {
		SentenceID      uint   `json:"sentence_id" binding:"required"`
		UserTranslation string `json:"user_translation" binding:"required"`
	}

	if err := c.ShouldBindJSON(&input); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	var word models.Word
	if err := h.db.First(&word, input.SentenceID).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			c.JSON(http.StatusNotFound, gin.H{"error": "Sentence not found"})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error fetching sentence"})
		return
	}

	// Simple exact match for now - could be enhanced with fuzzy matching or alternative translations
	isCorrect := input.UserTranslation == word.ExampleSentence.Korean

	// Record the attempt
	attempt := models.SentencePracticeAttempt{
		WordID:          word.ID,
		UserTranslation: input.UserTranslation,
		Correct:         isCorrect,
	}

	if err := h.db.Create(&attempt).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error recording attempt"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"correct":      isCorrect,
		"message":      getAttemptMessage(isCorrect),
		"alternatives": []string{word.ExampleSentence.Korean}, // Could be enhanced with alternative translations
	})
}

// GetSentenceExamples returns example sentences for a specific word
func (h *SentencePracticeHandler) GetSentenceExamples(c *gin.Context) {
	word := c.Query("word")
	if word == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Word parameter is required"})
		return
	}

	var words []models.Word
	if err := h.db.Where("hangul = ? OR romanization = ?", word, word).
		Where("example_sentence IS NOT NULL").
		Find(&words).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error fetching examples"})
		return
	}

	examples := make([]gin.H, 0)
	for _, w := range words {
		if w.ExampleSentence.Korean != "" {
			examples = append(examples, gin.H{
				"korean":  w.ExampleSentence.Korean,
				"english": w.ExampleSentence.English,
			})
		}
	}

	c.JSON(http.StatusOK, gin.H{
		"word":              word,
		"example_sentences": examples,
	})
}

// GetSentenceStatistics returns user's sentence practice statistics
func (h *SentencePracticeHandler) GetSentenceStatistics(c *gin.Context) {
	var totalAttempts, correctAttempts int64

	if err := h.db.Model(&models.SentencePracticeAttempt{}).Count(&totalAttempts).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error fetching statistics"})
		return
	}

	if err := h.db.Model(&models.SentencePracticeAttempt{}).Where("correct = ?", true).Count(&correctAttempts).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error fetching statistics"})
		return
	}

	var accuracyRate float64
	if totalAttempts > 0 {
		accuracyRate = float64(correctAttempts) / float64(totalAttempts) * 100
	}

	c.JSON(http.StatusOK, gin.H{
		"total_sentences_attempted": totalAttempts,
		"correct_answers":           correctAttempts,
		"accuracy_rate":             accuracyRate,
	})
}

func getAttemptMessage(correct bool) string {
	if correct {
		return "Correct! Well done!"
	}
	return "Not quite right. Try again!"
}
