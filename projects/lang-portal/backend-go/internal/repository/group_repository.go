package repository

import (
	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/models"
)

// GroupRepository defines the interface for group operations
type GroupRepository interface {
	ListGroups() ([]models.WordGroup, error)
	GetGroup(id uint) (*models.WordGroup, error)
	GetGroupWithWords(id uint) (*models.WordGroup, error)
	GetGroupStudySessions(groupID uint) ([]models.StudySession, error)
	Create(group *models.WordGroup) error
	Update(group *models.WordGroup) error
	Delete(id uint) error
}

// GroupRepositoryImpl implements GroupRepository
type GroupRepositoryImpl struct {
	*BaseRepository
}

// NewGroupRepository creates a new group repository instance
func NewGroupRepository(base *BaseRepository) GroupRepository {
	return &GroupRepositoryImpl{base}
}

// ListGroups returns all word groups
func (r *GroupRepositoryImpl) ListGroups() ([]models.WordGroup, error) {
	var groups []models.WordGroup
	if err := r.db.Find(&groups).Error; err != nil {
		return nil, err
	}
	return groups, nil
}

// GetGroup retrieves a group by ID
func (r *GroupRepositoryImpl) GetGroup(id uint) (*models.WordGroup, error) {
	var group models.WordGroup
	if err := r.db.First(&group, id).Error; err != nil {
		return nil, err
	}
	return &group, nil
}

// GetGroupWithWords retrieves a group with its associated words
func (r *GroupRepositoryImpl) GetGroupWithWords(id uint) (*models.WordGroup, error) {
	var group models.WordGroup
	if err := r.db.Preload("Words").First(&group, id).Error; err != nil {
		return nil, err
	}
	return &group, nil
}

// GetGroupStudySessions retrieves study sessions for a group
func (r *GroupRepositoryImpl) GetGroupStudySessions(groupID uint) ([]models.StudySession, error) {
	var sessions []models.StudySession
	if err := r.db.Where("word_group_id = ?", groupID). // Changed from group_id to word_group_id
								Preload("Activity").
								Order("completed_at DESC").
								Find(&sessions).Error; err != nil {
		return nil, err
	}
	return sessions, nil
}

// Create creates a new word group
func (r *GroupRepositoryImpl) Create(group *models.WordGroup) error {
	return r.db.Create(group).Error
}

// Update updates an existing word group
func (r *GroupRepositoryImpl) Update(group *models.WordGroup) error {
	return r.db.Save(group).Error
}

// Delete deletes a word group
func (r *GroupRepositoryImpl) Delete(id uint) error {
	return r.db.Delete(&models.WordGroup{}, id).Error
}
