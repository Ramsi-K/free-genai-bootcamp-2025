package models

import (
	"time"
)

// StudyActivity represents a learning activity type in the system
type StudyActivity struct {
	ID          uint      `gorm:"primaryKey" json:"id"`
	Name        string    `gorm:"not null;uniqueIndex" json:"name"`
	Description string    `json:"description"`
	Type        string    `json:"type"`
	Thumbnail   string    `json:"thumbnail"`
	LaunchURL   string    `gorm:"not null;column:launch_url" json:"launch_url"`
	CreatedAt   time.Time `json:"created_at"`
	UpdatedAt   time.Time `json:"updated_at"`
}
