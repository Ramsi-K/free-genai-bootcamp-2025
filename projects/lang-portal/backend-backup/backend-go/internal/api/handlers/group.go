package handlers

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"sort"
	"strconv"

	"github.com/gin-gonic/gin"
	"gorm.io/gorm"

	"github.com/Ramsi-K/free-genai-bootcamp-2025/projects/lang-portal/backend-go/internal/models"
)

// GroupHandler handles group-related requests
// It holds a reference to the database connection

type WordGroupMapping struct {
	Hangul     string   `json:"hangul"`
	GroupNames []string `json:"group_names"`
}

type GroupResponse struct {
	ID         uint   `json:"id"`
	Name       string `json:"group_name"`
	WordsCount int    `json:"word_count"`
}

type GroupHandler struct {
	db      *gorm.DB
	dataDir string // Directory containing word_groups.json
}

// NewGroupHandler creates a new instance of GroupHandler
func NewGroupHandler(db *gorm.DB) *GroupHandler {
	// Get the absolute path of the current directory (expected to be backend-go)
	cwd, err := filepath.Abs(".")
	if err != nil {
		cwd = "."
	}

	return &GroupHandler{
		db:      db,
		dataDir: cwd,
	}
}

// Get retrieves a specific group by its ID
func (h *GroupHandler) Get(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.ParseUint(idStr, 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid group ID"})
		return
	}

	// Load word-group mappings
	mappings, err := h.loadWordGroupMappings()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": fmt.Sprintf("failed to load word groups: %v", err)})
		return
	}

	// Get unique sorted group names
	groupCounts := make(map[string]int)
	var uniqueGroups []string
	for _, mapping := range mappings {
		for _, groupName := range mapping.GroupNames {
			if _, exists := groupCounts[groupName]; !exists {
				uniqueGroups = append(uniqueGroups, groupName)
			}
			groupCounts[groupName]++
		}
	}

	// Sort group names for consistent ordering
	sort.Strings(uniqueGroups)

	// Check if ID is valid
	if int(id) > len(uniqueGroups) || id < 1 {
		c.JSON(http.StatusNotFound, gin.H{"error": "Group not found"})
		return
	}

	groupName := uniqueGroups[id-1]
	c.JSON(http.StatusOK, GroupResponse{
		ID:         uint(id),
		Name:       groupName,
		WordsCount: groupCounts[groupName],
	})
}

// GetWords returns all words in a group
func (h *GroupHandler) GetWords(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.ParseUint(idStr, 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid group ID"})
		return
	}

	// Load word-group mappings
	mappings, err := h.loadWordGroupMappings()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": fmt.Sprintf("failed to load word groups: %v", err)})
		return
	}

	// Get unique sorted group names
	var uniqueGroups []string
	groupMap := make(map[string]bool)
	for _, mapping := range mappings {
		for _, groupName := range mapping.GroupNames {
			if !groupMap[groupName] {
				uniqueGroups = append(uniqueGroups, groupName)
				groupMap[groupName] = true
			}
		}
	}

	// Sort group names for consistent ordering
	sort.Strings(uniqueGroups)

	// Check if ID is valid
	if int(id) > len(uniqueGroups) || id < 1 {
		c.JSON(http.StatusNotFound, gin.H{"error": "Group not found"})
		return
	}

	groupName := uniqueGroups[id-1]

	// Find words in this group
	var wordsInGroup []string
	for _, mapping := range mappings {
		for _, name := range mapping.GroupNames {
			if name == groupName {
				wordsInGroup = append(wordsInGroup, mapping.Hangul)
				break
			}
		}
	}

	if len(wordsInGroup) == 0 {
		c.JSON(http.StatusOK, []models.Word{})
		return
	}

	// Get words from database
	var words []models.Word
	if err := h.db.Where("hangul IN ? AND deleted_at IS NULL", wordsInGroup).Find(&words).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to get words"})
		return
	}

	c.JSON(http.StatusOK, words)
}

// List returns all groups from word_groups.json
func (h *GroupHandler) List(c *gin.Context) {
	// Load word-group mappings
	mappings, err := h.loadWordGroupMappings()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": fmt.Sprintf("failed to load word groups: %v", err)})
		return
	}

	// Build a set of unique words for each group from the JSON mapping
	groupWordSet := make(map[string]map[string]bool)
	var uniqueGroups []string
	for _, mapping := range mappings {
		for _, groupName := range mapping.GroupNames {
			if _, exists := groupWordSet[groupName]; !exists {
				groupWordSet[groupName] = make(map[string]bool)
				uniqueGroups = append(uniqueGroups, groupName)
			}
			groupWordSet[groupName][mapping.Hangul] = true
		}
	}

	// Sort the group names for consistent ordering
	sort.Strings(uniqueGroups)

	// Build the response with the correct word counts per group
	response := make([]GroupResponse, len(uniqueGroups))
	for i, name := range uniqueGroups {
		response[i] = GroupResponse{
			ID:         uint(i + 1),
			Name:       name,
			WordsCount: len(groupWordSet[name]),
		}
	}

	c.JSON(http.StatusOK, response)
}

// GetStudySessions returns all study sessions for a group
func (h *GroupHandler) GetStudySessions(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.ParseUint(idStr, 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid group ID"})
		return
	}

	// Get study sessions with preloaded relationships
	var sessions []models.StudySession
	if err := h.db.Preload("Activity").
		Preload("Reviews").
		Where("group_id = ? AND deleted_at IS NULL", id).
		Find(&sessions).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to get study sessions"})
		return
	}

	// Format response with session stats
	type SessionResponse struct {
		models.StudySession
		Stats map[string]interface{} `json:"stats"`
	}

	var response []SessionResponse
	for _, session := range sessions {
		response = append(response, SessionResponse{
			StudySession: session,
			Stats:        session.GetStats(),
		})
	}

	c.JSON(http.StatusOK, response)
}

// Updated loadWordGroupMappings to load exclusively from backend-go/seed/word_groups.json
func (h *GroupHandler) loadWordGroupMappings() ([]WordGroupMapping, error) {
	filePath := filepath.Join(h.dataDir, "seed", "word_groups.json")
	data, err := os.ReadFile(filePath)
	if err != nil {
		return nil, fmt.Errorf("failed to read word_groups.json: %w", err)
	}
	var mappings []WordGroupMapping
	if err := json.Unmarshal(data, &mappings); err != nil {
		return nil, fmt.Errorf("failed to unmarshal word groups from %s: %w", filePath, err)
	}
	return mappings, nil
}
