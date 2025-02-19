package handlers

import (
	"net/http"
	"strconv"

	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/repository"
	"github.com/gin-gonic/gin"
)

// GroupHandler handles group-related requests
type GroupHandler struct {
	groupRepo *repository.GroupRepository
}

// NewGroupHandler creates a new group handler instance
func NewGroupHandler(repo *repository.GroupRepository) *GroupHandler {
	return &GroupHandler{groupRepo: repo}
}

// ListGroups returns all word groups
func (h *GroupHandler) ListGroups(c *gin.Context) {
	groups, err := h.groupRepo.ListGroups()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error fetching groups"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"data": groups})
}

// GetGroup returns details of a specific group
func (h *GroupHandler) GetGroup(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid group ID"})
		return
	}

	group, err := h.groupRepo.GetGroup(uint(id))
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Group not found"})
		return
	}

	c.JSON(http.StatusOK, group)
}

// GetGroupWords returns words belonging to a specific group
func (h *GroupHandler) GetGroupWords(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid group ID"})
		return
	}

	group, err := h.groupRepo.GetGroupWithWords(uint(id))
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Group not found"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"data": group.Words})
}

// GetGroupStudySessions returns study sessions for a specific group
func (h *GroupHandler) GetGroupStudySessions(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid group ID"})
		return
	}

	sessions, err := h.groupRepo.GetGroupStudySessions(uint(id))
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error fetching study sessions"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"data": sessions})
}
