package models

import (
	"database/sql/driver"
	"encoding/json"
	"errors"
	"time"
)

// ExampleSentence represents a Korean-English sentence pair
type ExampleSentence struct {
	Korean  string `json:"korean"`
	English string `json:"english"`
}

// Value implements the driver.Valuer interface for ExampleSentence
func (es ExampleSentence) Value() (driver.Value, error) {
	return json.Marshal(es)
}

// Scan implements the sql.Scanner interface for ExampleSentence
func (es *ExampleSentence) Scan(value interface{}) error {
	if value == nil {
		return nil
	}
	bytes, ok := value.([]byte)
	if !ok {
		return errors.New("invalid scan source for ExampleSentence")
	}
	return json.Unmarshal(bytes, es)
}

// StudyStatistics represents learning progress statistics
type StudyStatistics struct {
	CorrectCount int `json:"correct_count"`
	WrongCount   int `json:"wrong_count"`
}

// Value implements the driver.Valuer interface for StudyStatistics
func (ss StudyStatistics) Value() (driver.Value, error) {
	return json.Marshal(ss)
}

// Scan implements the sql.Scanner interface for StudyStatistics
func (ss *StudyStatistics) Scan(value interface{}) error {
	if value == nil {
		return nil
	}
	bytes, ok := value.([]byte)
	if !ok {
		return errors.New("invalid scan source for StudyStatistics")
	}
	return json.Unmarshal(bytes, ss)
}

// StringSlice is a custom type for handling string arrays in SQLite
type StringSlice []string

// Value implements the driver.Valuer interface for StringSlice
func (ss StringSlice) Value() (driver.Value, error) {
	return json.Marshal(ss)
}

// Scan implements the sql.Scanner interface for StringSlice
func (ss *StringSlice) Scan(value interface{}) error {
	if value == nil {
		return nil
	}
	bytes, ok := value.([]byte)
	if !ok {
		return errors.New("invalid scan source for StringSlice")
	}
	return json.Unmarshal(bytes, ss)
}

// Word represents a vocabulary word in the language learning system
type Word struct {
	ID              uint            `gorm:"primaryKey" json:"id"`
	Hangul          string          `gorm:"not null;uniqueIndex" json:"hangul"`
	Romanization    string          `gorm:"not null" json:"romanization"`
	Type            string          `gorm:"not null" json:"type"`
	English         StringSlice     `gorm:"type:text;not null" json:"english"`
	Groups          []WordGroup     `gorm:"many2many:group_words" json:"groups,omitempty"`
	ExampleSentence ExampleSentence `gorm:"type:text" json:"example_sentence"`
	StudyStatistics StudyStatistics `gorm:"type:text" json:"study_statistics"`
	CreatedAt       time.Time       `json:"created_at"`
	UpdatedAt       time.Time       `json:"updated_at"`
}
