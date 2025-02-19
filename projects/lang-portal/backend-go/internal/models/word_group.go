package models

import (
	"time"

	"gorm.io/gorm"
)

// WordGroup represents a thematic group of words
type WordGroup struct {
	ID          uint      `gorm:"primaryKey" json:"id"`
	Name        string    `gorm:"not null;uniqueIndex" json:"name"`
	Description string    `gorm:"not null" json:"description"`
	WordsCount  int       `gorm:"default:0" json:"words_count"`
	Words       []Word    `gorm:"many2many:group_words" json:"words,omitempty"`
	CreatedAt   time.Time `json:"created_at"`
	UpdatedAt   time.Time `json:"updated_at"`
}

// BeforeSave hook to update WordsCount
func (wg *WordGroup) BeforeSave(tx *gorm.DB) error {
	var count int64
	if err := tx.Model(&Word{}).
		Joins("JOIN group_words ON group_words.word_id = words.id").
		Where("group_words.word_group_id = ?", wg.ID).
		Count(&count).Error; err != nil {
		return err
	}
	wg.WordsCount = int(count)
	return nil
}
