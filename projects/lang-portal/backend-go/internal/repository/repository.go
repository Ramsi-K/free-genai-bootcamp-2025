package repository

import (
	"gorm.io/gorm"
)

// Repository provides an interface for database operations
type Repository interface {
	GetDB() *gorm.DB
}

// BaseRepository implements common repository functionality
type BaseRepository struct {
	db *gorm.DB
}

// NewBaseRepository creates a new base repository instance
func NewBaseRepository(db *gorm.DB) *BaseRepository {
	return &BaseRepository{db: db}
}

// GetDB returns the database instance
func (r *BaseRepository) GetDB() *gorm.DB {
	return r.db
}
