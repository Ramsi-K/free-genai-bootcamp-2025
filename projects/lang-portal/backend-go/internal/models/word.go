package models

import (
	"gorm.io/gorm"
)

// Join table for many-to-many relationship
type WordsGroups struct {
	WordID  uint `gorm:"primaryKey"`
	GroupID uint `gorm:"primaryKey"`
}

type Word struct {
	gorm.Model                  // Adds ID, CreatedAt, UpdatedAt, DeletedAt
	Hangul         string       `gorm:"not null" json:"hangul"`
	Romanization   string       `gorm:"not null" json:"romanization"`
	English        []string     `gorm:"serializer:json;not null" json:"english"`
	Type           string       `gorm:"not null" json:"type"`
	ExampleKorean  string       `json:"example_korean"`
	ExampleEnglish string       `json:"example_english"`
	Groups         []Group      `gorm:"many2many:words_groups;" json:"-"`
	Reviews        []WordReview `gorm:"foreignKey:WordID" json:"-"`
}

type Group struct {
	gorm.Model
	Name       string         `gorm:"not null" json:"name"`
	WordsCount int            `gorm:"default:0" json:"words_count"`
	Words      []Word         `gorm:"many2many:words_groups;" json:"-"`
	Sessions   []StudySession `gorm:"foreignKey:GroupID" json:"-"`
}

type StudySession struct {
	gorm.Model
	GroupID         uint          `gorm:"not null" json:"group_id"`
	StudyActivityID uint          `json:"study_activity_id"`
	Group           Group         `gorm:"foreignKey:GroupID" json:"-"`
	Activity        StudyActivity `gorm:"foreignKey:StudyActivityID" json:"-"`
	Reviews         []WordReview  `gorm:"foreignKey:StudySessionID" json:"-"`
}

type StudyActivity struct {
	gorm.Model
	Name         string         `gorm:"not null" json:"name"`
	URL          string         `gorm:"not null" json:"url"`
	ThumbnailURL string         `json:"thumbnail_url"`
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
