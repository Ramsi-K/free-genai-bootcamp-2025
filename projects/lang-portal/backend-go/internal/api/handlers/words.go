package handlers

import (
	"net/http"
	"strconv"

	"github.com/Ramsi-K/free-genai-bootcamp-2025/tree/main/projects/lang-portal/backend-go/internal/api/middleware"
	"github.com/Ramsi-K/free-genai-bootcamp-2025/tree/main/projects/lang-portal/backend-go/internal/models"

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
	var pagination middleware.Pagination
	if err := c.ShouldBindQuery(&pagination); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Validate pagination parameters
	if err := pagination.Validate(); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid page number"})
		return
	}

	var words []models.Word
	query := h.db.Model(&models.Word{}).Where("deleted_at IS NULL").Preload("Groups", "deleted_at IS NULL")

	// Apply sorting
	if pagination.SortBy != "" {
		order := pagination.SortBy
		if pagination.Order == "desc" {
			order += " DESC"
		} else {
			order += " ASC"
		}
		query = query.Order(order)
	}

	// Count total before pagination
	var total int64
	if err := query.Count(&total).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error counting words"})
		return
	}

	// Apply pagination
	offset := (pagination.GetPage() - 1) * pagination.GetLimit()
	query = query.Offset(offset).Limit(pagination.GetLimit())

	if err := query.Find(&words).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error fetching words"})
		return
	}

	// Extract group names for each word
	for i := range words {
		groupNames := make([]string, len(words[i].Groups))
		for j, group := range words[i].Groups {
			groupNames[j] = group.Name
		}
		words[i].WordGroups = groupNames
	}

	c.JSON(http.StatusOK, gin.H{
		"words": words,
		"pagination": gin.H{
			"current_page": pagination.GetPage(),
			"total_pages":  (total + int64(pagination.GetLimit()) - 1) / int64(pagination.GetLimit()),
			"total_items":  total,
			"per_page":     pagination.GetLimit(),
		},
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
	if err := h.db.Where("id = ? AND deleted_at IS NULL", id).
		Preload("Groups", "deleted_at IS NULL").
		First(&word).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			c.JSON(http.StatusNotFound, gin.H{"error": "Word not found"})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error fetching word"})
		return
	}

	// Extract group names for the response
	groupNames := make([]string, len(word.Groups))
	for i, group := range word.Groups {
		groupNames[i] = group.Name
	}
	word.WordGroups = groupNames

	c.JSON(http.StatusOK, word)
}
