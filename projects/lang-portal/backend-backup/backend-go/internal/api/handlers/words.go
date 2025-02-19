package handlers

import (
	"net/http"
	"strconv"

	"github.com/Ramsi-K/free-genai-bootcamp-2025/projects/lang-portal/backend-go/internal/models"

	"github.com/gin-gonic/gin"
	"gorm.io/gorm"
)

type WordHandler struct {
	db *gorm.DB
}

func NewWordHandler(db *gorm.DB) *WordHandler {
	return &WordHandler{db: db}
}

func (h *WordHandler) List(c *gin.Context) {
	var words []models.Word
	// Parse pagination parameters
	pageStr := c.DefaultQuery("page", "1")
	perPageStr := c.DefaultQuery("per_page", "100")
	page, err := strconv.Atoi(pageStr)
	if err != nil || page < 1 {
		page = 1
	}
	perPage, err := strconv.Atoi(perPageStr)
	if err != nil || perPage < 1 {
		perPage = 100
	}
	offset := (page - 1) * perPage

	// Get total count
	var total int64
	err = h.db.Model(&models.Word{}).Distinct("words.id").Count(&total).Error
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to count words"})
		return
	}

	// Query words with pagination, ensuring distinct results
	err = h.db.Model(&models.Word{}).Distinct("words.id").Order("id asc").Offset(offset).Limit(perPage).Find(&words).Error
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to load words"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"words":    words,
		"total":    total,
		"page":     page,
		"per_page": perPage,
	})
}

func (h *WordHandler) Get(c *gin.Context) {
	id := c.Param("id")

	// Validate ID is numeric
	if _, err := strconv.ParseUint(id, 10, 64); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid ID format"})
		return
	}

	var word models.Word
	if err := h.db.Where("id = ? AND deleted_at IS NULL", id).First(&word).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			c.JSON(http.StatusNotFound, gin.H{"error": "Word not found"})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error fetching word"})
		return
	}

	c.JSON(http.StatusOK, word)
}
