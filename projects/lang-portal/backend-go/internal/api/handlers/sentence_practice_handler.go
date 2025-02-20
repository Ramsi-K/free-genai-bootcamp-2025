package handlers

import (
	"net/http"

	"strconv"

	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/repository"
	"github.com/gin-gonic/gin"
)

// SentencePracticeHandler handles sentence practice-related requests
type SentencePracticeHandler struct {
	wordRepo repository.WordRepository
}

// NewSentencePracticeHandler creates a new sentence practice handler instance
func NewSentencePracticeHandler(wordRepo repository.WordRepository) *SentencePracticeHandler {
	return &SentencePracticeHandler{wordRepo: wordRepo}
}

// PracticeSentenceResponse defines the structure for sentence practice response
type PracticeSentenceResponse struct {
	Word             string   `json:"word"`
	ExampleSentences []string `json:"example_sentences"`
}

// GetPracticeSentence returns a practice sentence for a given word
func (h *SentencePracticeHandler) GetPracticeSentence(c *gin.Context) {
	c.JSON(http.StatusNotImplemented, gin.H{"error": "GetPracticeSentence not implemented"})
}

// GetSentenceExamples returns example sentences for a given word
func (h *SentencePracticeHandler) GetSentenceExamples(c *gin.Context) {
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

	response := PracticeSentenceResponse{
		Word:             word.Hangul,
		ExampleSentences: []string{word.Sentences[0].Korean, word.Sentences[0].English},
	}

	c.JSON(http.StatusOK, response)
}
