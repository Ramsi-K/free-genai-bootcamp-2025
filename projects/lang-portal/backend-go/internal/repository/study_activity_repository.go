package repository

import (
	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/models"
)

// StudyActivityRepository handles database operations for study activities
type StudyActivityRepository struct {
	*BaseRepository
}

// NewStudyActivityRepository creates a new study activity repository instance
func NewStudyActivityRepository(base *BaseRepository) *StudyActivityRepository {
	return &StudyActivityRepository{base}
}

// ListActivities returns all study activities
func (r *StudyActivityRepository) ListActivities() ([]models.StudyActivity, error) {
	var activities []models.StudyActivity
	if err := r.db.Find(&activities).Error; err != nil {
		return nil, err
	}
	return activities, nil
}

// GetActivity retrieves a study activity by ID
func (r *StudyActivityRepository) GetActivity(id uint) (*models.StudyActivity, error) {
	var activity models.StudyActivity
	if err := r.db.First(&activity, id).Error; err != nil {
		return nil, err
	}
	return &activity, nil
}

// GetLastStudySession gets the most recent study session
func (r *StudyActivityRepository) GetLastStudySession() (*models.StudySession, error) {
	var session models.StudySession
	if err := r.db.Preload("StudyActivity").
		Order("completed_at DESC").
		First(&session).Error; err != nil {
		return nil, err
	}
	return &session, nil
}

func (r *StudyActivityRepository) CreateStudySession(session *models.StudySession) error {
	result := r.db.Create(session)
	if result.Error != nil {
		return result.Error
	}

	// Load the related activity and word group
	return r.db.Preload("StudyActivity").
		Preload("WordGroup").
		First(session, session.ID).Error
}

func (r *StudyActivityRepository) GetGroupStudySessions(groupID uint) ([]models.StudySession, error) {
	var sessions []models.StudySession
	err := r.db.Where("word_group_id = ?", groupID).
		Preload("StudyActivity").
		Order("created_at DESC").
		Find(&sessions).Error
	return sessions, err
}

func (r *StudyActivityRepository) GetStudyProgress() (map[string]interface{}, error) {
	var stats struct {
		TotalWords    int64   `json:"total_words"`
		StudiedWords  int64   `json:"studied_words"`
		SuccessRate   float64 `json:"success_rate"`
		TotalSessions int64   `json:"total_sessions"`
	}

	// Get total words
	if err := r.db.Model(&models.Word{}).Count(&stats.TotalWords).Error; err != nil {
		return nil, err
	}

	// Get studied words (words with at least one review)
	if err := r.db.Model(&models.Word{}).
		Where("correct_count > 0 OR wrong_count > 0").
		Count(&stats.StudiedWords).Error; err != nil {
		return nil, err
	}

	// Calculate success rate
	var totalCorrect, totalAttempts int64
	if err := r.db.Model(&models.StudySession{}).
		Select("SUM(correct_count) as total_correct, SUM(correct_count + wrong_count) as total_attempts").
		Row().Scan(&totalCorrect, &totalAttempts); err != nil {
		return nil, err
	}

	if totalAttempts > 0 {
		stats.SuccessRate = float64(totalCorrect) / float64(totalAttempts) * 100
	}

	// Get total sessions
	if err := r.db.Model(&models.StudySession{}).Count(&stats.TotalSessions).Error; err != nil {
		return nil, err
	}

	return map[string]interface{}{
		"total_words":    stats.TotalWords,
		"studied_words":  stats.StudiedWords,
		"success_rate":   stats.SuccessRate,
		"total_sessions": stats.TotalSessions,
	}, nil
}

// GetQuickStats retrieves quick learning statistics
func (r *StudyActivityRepository) GetQuickStats() (map[string]any, error) {
	var totalSessions int64
	var activeGroups int64
	var successRate float64
	var studiedGroups int64

	if err := r.db.Model(&models.StudySession{}).Count(&totalSessions).Error; err != nil {
		return nil, err
	}

	if err := r.db.Model(&models.WordGroup{}).
		Joins("JOIN study_sessions ON study_sessions.group_id = word_groups.id").
		Distinct("word_groups.id").
		Count(&activeGroups).Error; err != nil {
		return nil, err
	}

	// Calculate success rate
	var totalCorrect, totalAttempts int64
	if err := r.db.Model(&models.StudySession{}).
		Select("SUM(correct_count) as total_correct, SUM(correct_count + wrong_count) as total_attempts").
		Row().Scan(&totalCorrect, &totalAttempts); err != nil {
		return nil, err
	}

	if totalAttempts > 0 {
		successRate = float64(totalCorrect) / float64(totalAttempts) * 100
	}

	return map[string]interface{}{
		"total_sessions": totalSessions,
		"active_groups":  activeGroups,
		"success_rate":   successRate,
		"studied_groups": studiedGroups,
	}, nil
}

// GetStudySession retrieves a study session by ID
func (r *StudyActivityRepository) GetStudySession(id uint) (*models.StudySession, error) {
	var session models.StudySession
	if err := r.db.Preload("StudyActivity").Preload("WordGroup").First(&session, id).Error; err != nil {
		return nil, err
	}
	return &session, nil
}
