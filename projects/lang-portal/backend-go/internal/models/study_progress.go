package models

import (
	"time"

	"gorm.io/gorm"
)

type StudyProgress struct {
	ID             uint           `json:"id" gorm:"primaryKey"`
	GroupID        uint           `json:"group_id"`
	WordGroup      *WordGroup     `json:"word_group,omitempty" gorm:"foreignKey:GroupID"`
	TotalWords     int            `json:"total_words"`
	CompletedWords int            `json:"completed_words"`
	LastStudyDate  time.Time      `json:"last_study_date"`
	CreatedAt      time.Time      `json:"created_at"`
	UpdatedAt      time.Time      `json:"updated_at"`
	DeletedAt      gorm.DeletedAt `json:"deleted_at,omitempty" gorm:"index"`
}

func (sp *StudyProgress) TableName() string {
	return "study_progress"
}
