package repository

import (
	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/models"
)

// GroupRepository handles database operations for word groups
type GroupRepository struct {
	*BaseRepository
}

// NewGroupRepository creates a new group repository instance
func NewGroupRepository(base *BaseRepository) *GroupRepository {
	return &GroupRepository{base}
}

// ListGroups returns all word groups
func (r *GroupRepository) ListGroups() ([]models.WordGroup, error) {
	var groups []models.WordGroup
	if err := r.db.Find(&groups).Error; err != nil {
		return nil, err
	}
	return groups, nil
}

// GetGroup retrieves a group by ID
func (r *GroupRepository) GetGroup(id uint) (*models.WordGroup, error) {
	var group models.WordGroup
	if err := r.db.First(&group, id).Error; err != nil {
		return nil, err
	}
	return &group, nil
}

// GetGroupWithWords retrieves a group with its associated words
func (r *GroupRepository) GetGroupWithWords(id uint) (*models.WordGroup, error) {
	var group models.WordGroup
	if err := r.db.Preload("Words").First(&group, id).Error; err != nil {
		return nil, err
	}
	return &group, nil
}

// GetGroupStudySessions retrieves study sessions for a group
func (r *GroupRepository) GetGroupStudySessions(groupID uint) ([]models.StudySession, error) {
	var sessions []models.StudySession
	if err := r.db.Where("group_id = ?", groupID).
		Preload("Activity").
		Order("completed_at DESC").
		Find(&sessions).Error; err != nil {
		return nil, err
	}
	return sessions, nil
}
