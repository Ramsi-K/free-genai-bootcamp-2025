package models

import "time"

// DashboardData represents the complete dashboard response
type DashboardData struct {
	LastStudySession *LastStudySession `json:"last_study_session"`
	StudyProgress    StudyProgress     `json:"study_progress"`
	QuickStats       QuickStats        `json:"quick_stats"`
}

// LastStudySession represents the last study activity
type LastStudySession struct {
	ActivityName string    `json:"activity_name"`
	GroupName    string    `json:"group_name"`
	Timestamp    time.Time `json:"timestamp"`
	Stats        struct {
		CorrectCount int `json:"correct_count"`
		WrongCount   int `json:"wrong_count"`
	} `json:"stats"`
	GroupID uint `json:"group_id"`
}

// StudyProgress represents overall progress
type StudyProgress struct {
	WordsStudied    int     `json:"words_studied"`
	TotalWords      int     `json:"total_words"`
	MasteryProgress float64 `json:"mastery_progress"`
}

// QuickStats represents quick statistics
type QuickStats struct {
	SuccessRate       float64 `json:"success_rate"`
	TotalSessions     int     `json:"total_sessions"`
	TotalActiveGroups int     `json:"total_active_groups"`
	StudyStreak       int     `json:"study_streak"`
}
