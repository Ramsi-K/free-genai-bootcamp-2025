package models

import (
	"time"

	"gorm.io/gorm"
)

// Word represents a vocabulary word in the language learning system
type Word struct {
	ID                  uint          `gorm:"primaryKey" json:"id"`
	Hangul              string        `gorm:"not null;uniqueIndex" json:"hangul"`
	Romanization        string        `gorm:"not null" json:"romanization"`
	Type                string        `gorm:"not null" json:"type"`
	EnglishTranslations []Translation `gorm:"foreignKey:WordID" json:"-"`
	English             []string      `gorm:"-" json:"english"`
	Sentences           []Sentence    `gorm:"foreignKey:WordID" json:"sentences,omitempty"`
	Groups              []WordGroup   `gorm:"many2many:group_words" json:"groups,omitempty"`
	CorrectCount        int           `gorm:"default:0" json:"correct_count"`
	WrongCount          int           `gorm:"default:0" json:"wrong_count"`
	CreatedAt           time.Time     `json:"created_at"`
	UpdatedAt           time.Time     `json:"updated_at"`
}

// Translation represents an English translation for a Korean word
type Translation struct {
	ID        uint      `gorm:"primaryKey" json:"id"`
	WordID    uint      `gorm:"not null;index" json:"word_id"`
	Hangul    string    `gorm:"not null" json:"hangul"`
	English   string    `gorm:"not null" json:"english"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

// Sentence represents an example sentence for a word

// ExampleSentence represents an example sentence for a word
type Sentence struct {
	ID        uint      `gorm:"primaryKey" json:"id"`
	WordID    uint      `gorm:"not null;index" json:"word_id"`
	Word      Word      `gorm:"foreignKey:WordID" json:"word"`
	Korean    string    `gorm:"not null" json:"korean"`
	English   string    `gorm:"not null" json:"english"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

// AfterFind GORM hook to convert EnglishTranslations to English string slice
func (w *Word) AfterFind(tx *gorm.DB) error {
	if len(w.EnglishTranslations) > 0 {
		w.English = make([]string, len(w.EnglishTranslations))
		for i, t := range w.EnglishTranslations {
			w.English[i] = t.English
		}
	}
	return nil
}
