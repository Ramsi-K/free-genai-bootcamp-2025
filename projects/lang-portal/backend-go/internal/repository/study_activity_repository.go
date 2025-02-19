package repository

import (
	"time"

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

// CreateStudySession creates a new study session
func (r *StudyActivityRepository) CreateStudySession(session *models.StudySession) error {
	session.CreatedAt = time.Now()
	session.UpdatedAt = time.Now()
	return r.db.Create(session).Error
}

// GetLastStudySession retrieves the most recent study session
func (r *StudyActivityRepository) GetLastStudySession() (*models.StudySession, error) {
	var session models.StudySession
	if err := r.db.Preload("Group").Preload("Activity").
		Order("completed_at DESC").
		First(&session).Error; err != nil {
		return nil, err
	}
	return &session, nil
}

// GetStudyProgress retrieves overall study progress
func (r *StudyActivityRepository) GetStudyProgress() (map[string]interface{}, error) {
	var totalWords int64
	var studiedWords int64
	var successRate float64

	if err := r.db.Model(&models.Word{}).Count(&totalWords).Error; err != nil {
		return nil, err
	}

	if err := r.db.Model(&models.Word{}).
		Where("study_statistics->>'correct_count' > ?", 0).
		Count(&studiedWords).Error; err != nil {
		return nil, err
	}

	// Calculate success rate from study sessions
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
		"total_words":    totalWords,
		"studied_words":  studiedWords,
		"success_rate":   successRate,
		"total_correct":  totalCorrect,
		"total_attempts": totalAttempts,
	}, nil
}

// GetQuickStats retrieves quick learning statistics
func (r *StudyActivityRepository) GetQuickStats() (map[string]interface{}, error) {
	var totalSessions int64
	var activeGroups int64
	var successRate float64

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
	}, nil
}
