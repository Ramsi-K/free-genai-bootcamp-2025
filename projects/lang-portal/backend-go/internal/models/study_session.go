package models

import (
	"time"
)

// StudySession represents a single study session for a word
type StudySession struct {
	ID         uint          `gorm:"primaryKey" json:"id"`
	WordID     uint          `gorm:"index" json:"word_id"` //  word id
	Correct    bool          `json:"correct"`              //  attempt was correct
	ActivityID uint          `gorm:"index" json:"activity_id"`
	Activity   StudyActivity `gorm:"foreignKey:ActivityID" json:"activity,omitempty"`
	CreatedAt  time.Time     `json:"created_at"`
	UpdatedAt  time.Time     `json:"updated_at"`
}
