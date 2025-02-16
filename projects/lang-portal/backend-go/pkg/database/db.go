package database

import (
	"fmt"
	"log"
	"os"
	"path/filepath"

	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
	"github.com/yourusername/lang-portal/internal/models"
)

func SetupDB() (*gorm.DB, error) {
	// Ensure instance directory exists
	if err := os.MkdirAll("instance", 0755); err != nil {
		return nil, fmt.Errorf("failed to create instance directory: %v", err)
	}

	dbPath := filepath.Join("instance", "words.db")
	
	// Configure GORM with SQLite
	config := &gorm.Config{
		Logger: logger.Default.LogMode(logger.Info),
	}
	
	db, err := gorm.Open(sqlite.Open(dbPath), config)
	if err != nil {
		return nil, fmt.Errorf("failed to connect to database: %v", err)
	}

	// Auto Migrate the schema
	if err := db.AutoMigrate(
		&models.Word{},
		&models.Group{},
		&models.StudySession{},
		&models.StudyActivity{},
		&models.WordReview{},
		&models.WordsGroups{},
	); err != nil {
		return nil, fmt.Errorf("failed to migrate database: %v", err)
	}

	return db, nil
} 