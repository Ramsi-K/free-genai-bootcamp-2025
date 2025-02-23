package models

import (
	"time"

	"gorm.io/gorm"
)

// StudySession represents a study session
type StudySession struct {
	gorm.Model
	WordGroupID     *uint         `json:"word_group_id" gorm:"column:word_group_id"` // Changed from group_id
	StudyActivityID uint          `json:"study_activity_id"`
	StudyActivity   StudyActivity `gorm:"foreignKey:StudyActivityID" json:"study_activity"`
	CorrectCount    int           `json:"correct_count"`
	WrongCount      int           `json:"wrong_count"`
	CompletedAt     time.Time     `json:"completed_at"`
}
