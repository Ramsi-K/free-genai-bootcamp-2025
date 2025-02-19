package models

import (
	"time"
)

// StudySession represents a single study session for a word group
type StudySession struct {
	ID           uint          `gorm:"primaryKey" json:"id"`
	GroupID      uint          `gorm:"index" json:"group_id"`
	Group        WordGroup     `gorm:"foreignKey:GroupID" json:"group,omitempty"`
	ActivityID   uint          `gorm:"index" json:"activity_id"`
	Activity     StudyActivity `gorm:"foreignKey:ActivityID" json:"activity,omitempty"`
	CorrectCount int           `json:"correct_count"`
	WrongCount   int           `json:"wrong_count"`
	CompletedAt  time.Time     `json:"completed_at"`
	CreatedAt    time.Time     `json:"created_at"`
	UpdatedAt    time.Time     `json:"updated_at"`
}
