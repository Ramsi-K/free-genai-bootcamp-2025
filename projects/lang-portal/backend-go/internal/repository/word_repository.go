package repository

import (
	"log"

	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/models"
	"gorm.io/gorm"
)

// WordRepository defines the interface for word operations
type WordRepository interface {
	ListWords(page, limit int) ([]models.Word, int64, error)
	GetWord(id uint) (*models.Word, error)
	GetWordsByGroup(groupID uint) ([]models.Word, error)
	GetDB() *gorm.DB
}

// WordRepositoryImpl implements WordRepository
type WordRepositoryImpl struct {
	*BaseRepository
}

// NewWordRepository creates a new word repository instance
func NewWordRepository(base *BaseRepository) WordRepository {
	return &WordRepositoryImpl{base}
}

// ListWords returns a paginated list of words
// In word_repository.go
func (r *WordRepositoryImpl) ListWords(page, limit int) ([]models.Word, int64, error) {
	var words []models.Word
	var total int64
	offset := (page - 1) * limit

	// Ensure preloading works
	query := r.db.Model(&models.Word{}).
		Preload("EnglishTranslations").
		Preload("Sentences")

	if err := query.Count(&total).Error; err != nil {
		log.Printf("Error counting words: %v", err)
		return nil, 0, err
	}

	if err := query.Offset(offset).Limit(limit).Find(&words).Error; err != nil {
		log.Printf("Error finding words: %v", err)
		return nil, 0, err
	}

	log.Printf("Found %d words, total %d", len(words), total)
	return words, total, nil
}

// GetWord retrieves a word by ID
func (r *WordRepositoryImpl) GetWord(id uint) (*models.Word, error) {
	var word models.Word
	result := r.db.Preload("Sentences").First(&word, id)
	if result.Error != nil {
		return nil, result.Error
	}
	return &word, nil
}

// GetWordsByGroup retrieves words belonging to a specific group
func (r *WordRepositoryImpl) GetWordsByGroup(groupID uint) ([]models.Word, error) {
	var words []models.Word
	if err := r.db.Joins("JOIN group_words ON group_words.word_id = words.id").
		Where("group_words.word_group_id = ?", groupID).
		Find(&words).Error; err != nil {
		return nil, err
	}
	return words, nil
}

func (r *WordRepositoryImpl) GetDB() *gorm.DB {
	return r.db
}
