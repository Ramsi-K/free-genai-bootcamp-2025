package models

import (
	"time"

	"gorm.io/gorm"
)

type QuickStats struct {
	ID             uint           `json:"id" gorm:"primaryKey"`
	GroupsStudied  int            `json:"groups_studied"`
	TotalSessions  int            `json:"total_sessions"`
	CorrectAnswers int            `json:"correct_answers"`
	WrongAnswers   int            `json:"wrong_answers"`
	CreatedAt      time.Time      `json:"created_at"`
	UpdatedAt      time.Time      `json:"updated_at"`
	DeletedAt      gorm.DeletedAt `json:"deleted_at,omitempty" gorm:"index"`
}

func (qs *QuickStats) TableName() string {
	return "quick_stats"
}
