package models

import (
	"encoding/json"
	"time"

	"gorm.io/gorm"
)

// Join table for many-to-many relationship
type WordsGroups struct {
	WordID  uint `gorm:"primaryKey"`
	GroupID uint `gorm:"primaryKey"`
}

type Word struct {
	gorm.Model                   // Adds ID, CreatedAt, UpdatedAt, DeletedAt
	Hangul          string       `gorm:"not null" json:"hangul"`
	Romanization    string       `gorm:"not null" json:"romanization"`
	English         []string     `gorm:"serializer:json;not null" json:"english"`
	Type            string       `gorm:"not null" json:"type"`
	WordGroups      []string     `gorm:"-" json:"word_groups"` // Transient field for group names
	ExampleSentence Example      `gorm:"embedded" json:"example"`
	Groups          []Group      `gorm:"many2many:words_groups;" json:"word_groups,omitempty"`
	Reviews         []WordReview `gorm:"foreignKey:WordID" json:"-"`
}

type Example struct {
	Korean  string `json:"korean"`
	English string `json:"english"`
}

type Group struct {
	gorm.Model
	Name       string         `gorm:"not null" json:"group_name"`
	WordsCount int            `gorm:"default:0" json:"word_count"`
	Words      []Word         `gorm:"many2many:words_groups;" json:"words,omitempty"`
	Sessions   []StudySession `gorm:"foreignKey:GroupID" json:"-"`
}

// BeforeSave hook to update WordsCount
func (g *Group) BeforeSave(tx *gorm.DB) error {
	if len(g.Words) > 0 {
		g.WordsCount = len(g.Words)
	}
	return nil
}

// MarshalJSON implements custom JSON marshaling for Group
func (g *Group) MarshalJSON() ([]byte, error) {
	type Alias Group
	return json.Marshal(&struct {
		*Alias
		TotalWordCount int `json:"total_word_count"`
	}{
		Alias:          (*Alias)(g),
		TotalWordCount: g.WordsCount,
	})
}

type StudySession struct {
	gorm.Model
	GroupID         uint          `gorm:"not null" json:"group_id"`
	StudyActivityID uint          `gorm:"not null" json:"study_activity_id"`
	Group           Group         `gorm:"foreignKey:GroupID" json:"group"`
	Activity        StudyActivity `gorm:"foreignKey:StudyActivityID" json:"activity"`
	Reviews         []WordReview  `gorm:"foreignKey:StudySessionID" json:"reviews,omitempty"`
	CompletedAt     *time.Time    `json:"completed_at"`
}

// GetStats returns the statistics for this study session
func (s *StudySession) GetStats() map[string]interface{} {
	var correct, wrong int
	for _, review := range s.Reviews {
		if review.Correct {
			correct++
		} else {
			wrong++
		}
	}

	return map[string]interface{}{
		"correct_count": correct,
		"wrong_count":   wrong,
		"success_rate":  float64(correct) / float64(correct+wrong) * 100,
	}
}

type StudyActivity struct {
	gorm.Model
	Name         string         `gorm:"not null" json:"name"`
	Description  string         `json:"description"`
	ThumbnailURL string         `json:"thumbnail_url"`
	Type         string         `gorm:"not null" json:"type"`
	Sessions     []StudySession `gorm:"foreignKey:StudyActivityID" json:"-"`
}

type WordReview struct {
	gorm.Model
	WordID         uint         `gorm:"not null" json:"word_id"`
	StudySessionID uint         `gorm:"not null" json:"study_session_id"`
	Correct        bool         `gorm:"not null" json:"correct"`
	Word           Word         `gorm:"foreignKey:WordID" json:"-"`
	StudySession   StudySession `gorm:"foreignKey:StudySessionID" json:"-"`
}

// StudyStatistics returns the correct and wrong counts for this word
func (w *Word) StudyStatistics() map[string]int {
	var correct, wrong int
	for _, review := range w.Reviews {
		if review.Correct {
			correct++
		} else {
			wrong++
		}
	}
	return map[string]int{
		"correct_count": correct,
		"wrong_count":   wrong,
	}
}

// MarshalJSON implements custom JSON marshaling
func (w *Word) MarshalJSON() ([]byte, error) {
	type Alias Word
	stats := w.StudyStatistics()
	return json.Marshal(&struct {
		*Alias
		StudyStatistics map[string]int `json:"study_statistics,omitempty"`
	}{
		Alias:           (*Alias)(w),
		StudyStatistics: stats,
	})
}

type SentencePracticeAttempt struct {
	ID              uint   `gorm:"primaryKey"`
	WordID          uint   `gorm:"not null;index"`
	Word            Word   `gorm:"foreignKey:WordID"`
	UserTranslation string `gorm:"not null"`
	Correct         bool   `gorm:"not null"`
	CreatedAt       time.Time
	UpdatedAt       time.Time
}
