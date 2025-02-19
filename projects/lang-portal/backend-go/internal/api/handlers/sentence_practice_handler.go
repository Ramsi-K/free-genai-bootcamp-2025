package handlers

import (
	"net/http"

	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/repository"
	"github.com/gin-gonic/gin"
)

// SentencePracticeHandler handles sentence practice-related requests
type SentencePracticeHandler struct {
	wordRepo repository.WordRepository
}

// NewSentencePracticeHandler creates a new sentence practice handler instance
func NewSentencePracticeHandler(repo repository.WordRepository) *SentencePracticeHandler {
	return &SentencePracticeHandler{wordRepo: repo}
}

// GetPracticeSentence returns a random sentence for practice
func (h *SentencePracticeHandler) GetPracticeSentence(c *gin.Context) {
	// Get a random word with example sentence
	words, _, err := h.wordRepo.ListWords(1, 1)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error fetching practice sentence"})
		return
	}

	if len(words) == 0 {
		c.JSON(http.StatusNotFound, gin.H{"error": "No practice sentences available"})
		return
	}

	word := words[0]
	c.JSON(http.StatusOK, gin.H{
		"word": gin.H{
			"hangul":       word.Hangul,
			"romanization": word.Romanization,
			"english":      word.English,
		},
		"example_sentence": word.ExampleSentence,
	})
}

// GetSentenceExamples returns example sentences for a specific word
func (h *SentencePracticeHandler) GetSentenceExamples(c *gin.Context) {
	word := c.Query("word")
	if word == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Word parameter is required"})
		return
	}

	// Find word by Hangul
	words, _, err := h.wordRepo.ListWords(1, 1)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error fetching examples"})
		return
	}

	if len(words) == 0 {
		c.JSON(http.StatusNotFound, gin.H{"error": "Word not found"})
		return
	}

	// For now, just return the example sentence from the word
	// In a real implementation, we would have multiple examples per word
	c.JSON(http.StatusOK, gin.H{
		"word": word,
		"example_sentences": []gin.H{
			{
				"korean":  words[0].ExampleSentence.Korean,
				"english": words[0].ExampleSentence.English,
			},
		},
	})
}
