package models

import (
	"time"

	"gorm.io/gorm"
)

type StudySession struct {
	gorm.Model
	WordGroupID     uint             `json:"word_group_id" gorm:"column:word_group_id"`
	WordGroup       WordGroup        `gorm:"foreignKey:WordGroupID" json:"word_group,omitempty"`
	StudyActivityID uint             `json:"study_activity_id" gorm:"column:study_activity_id"`
	StudyActivity   StudyActivity    `gorm:"foreignKey:StudyActivityID" json:"study_activity,omitempty"`
	CorrectCount    int              `json:"correct_count"`
	WrongCount      int              `json:"wrong_count"`
	CompletedAt     time.Time        `json:"completed_at"`
	ReviewItems     []WordReviewItem `gorm:"foreignKey:StudySessionID" json:"review_items,omitempty"`
}
