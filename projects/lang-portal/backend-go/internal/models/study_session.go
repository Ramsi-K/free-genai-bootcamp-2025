package models

import (
	"time"

	"gorm.io/gorm"
)

// StudySession represents a study session
type StudySession struct {
	gorm.Model
	StudyActivityID uint          `json:"study_activity_id"`
	StudyActivity   StudyActivity `gorm:"foreignKey:StudyActivityID" json:"study_activity"`
	WordGroupID     *uint         `json:"word_group_id"` // Optional: ID of the word group being studied
	CorrectCount    int           `json:"correct_count"`
	WrongCount      int           `json:"wrong_count"`
	CompletedAt     time.Time     `json:"completed_at"`
}
