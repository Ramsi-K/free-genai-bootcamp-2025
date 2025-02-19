package handlers

import (
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"gorm.io/gorm"

	"github.com/Ramsi-K/free-genai-bootcamp-2025/tree/main/projects/lang-portal/backend-go/internal/models"
)

// Get retrieves a specific group by its ID
func (h *GroupHandler) Get(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.Atoi(idStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid group ID"})
		return
	}

	var group models.Group
	if err := h.db.Where("id = ? AND deleted_at IS NULL", id).First(&group).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			c.JSON(http.StatusNotFound, gin.H{"error": "Group not found"})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error fetching group"})
		return
	}

	c.JSON(http.StatusOK, group)
}

// GetWords returns the words belonging to a specific group
func (h *GroupHandler) GetWords(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.Atoi(idStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid group ID"})
		return
	}

	var group models.Group
	// Preload the Words association with filter
	if err := h.db.Where("id = ? AND deleted_at IS NULL", id).
		Preload("Words", "deleted_at IS NULL").
		First(&group).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			c.JSON(http.StatusNotFound, gin.H{"error": "Group not found"})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error fetching group words"})
		return
	}

	c.JSON(http.StatusOK, group.Words)
}

// List returns all groups that are not soft-deleted
func (h *GroupHandler) List(c *gin.Context) {
	var groups []models.Group
	if err := h.db.Where("deleted_at IS NULL").Find(&groups).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error fetching groups"})
		return
	}
	c.JSON(http.StatusOK, groups)
}
