package models

import (
	"time"
)

// WordReviewItem represents a single word review in a study session
type WordReviewItem struct {
	ID             uint         `gorm:"primaryKey" json:"id"`
	WordID         uint         `gorm:"index" json:"word_id"`
	Word           Word         `gorm:"foreignKey:WordID" json:"word,omitempty"`
	StudySessionID uint         `gorm:"index" json:"study_session_id"`
	StudySession   StudySession `gorm:"foreignKey:StudySessionID" json:"study_session,omitempty"`
	CorrectCount   int          `json:"correct_count"`
	WrongCount     int          `json:"wrong_count"`
	CreatedAt      time.Time    `json:"created_at"`
}
