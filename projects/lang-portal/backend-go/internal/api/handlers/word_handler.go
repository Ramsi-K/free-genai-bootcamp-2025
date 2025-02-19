package handlers

import (
	"net/http"
	"strconv"

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

// ListWords returns a paginated list of words
func (h *WordHandler) ListWords(c *gin.Context) {
	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "10"))

	words, total, err := h.wordRepo.ListWords(page, limit)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error fetching words"})
		return
	}

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
