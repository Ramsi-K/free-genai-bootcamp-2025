package database

import (
	"log"
	"os"

	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/models"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

var DB *gorm.DB

// Initialize sets up the database connection and runs migrations
func Initialize() error {
	var err error

	// Database URI
	dbURI := os.Getenv("DATABASE_URL")
	if dbURI == "" {
		dbURI = "lang_portal.db" // Default SQLite file
	}

	// Configure logging
	newLogger := logger.New(
		log.New(os.Stdout, "\r\n", log.LstdFlags), // io writer
		logger.Config{
			SlowThreshold:             0,           // Disable slow SQL threshold
			LogLevel:                  logger.Info, // Log level
			IgnoreRecordNotFoundError: false,       // Ignore ErrRecordNotFound error
			Colorful:                  true,        // Enable color
		},
	)

	// Configure GORM with detailed logging
	config := &gorm.Config{
		Logger: newLogger,
	}

	DB, err = gorm.Open(sqlite.Open(dbURI), config)
	if err != nil {
		return err
	}

	// Run migrations
	err = DB.AutoMigrate(
		&models.Translation{},
		&models.Sentence{},
		&models.Word{},
		&models.WordGroup{},
		&models.GROUP_Word{},
		&models.GROUP_Translation{},
		&models.StudyActivity{},
		&models.StudySession{},
		&models.WordReviewItem{},
	)
	if err != nil {
		return err
	}

	// Check if database needs seeding
	var wordCount, groupCount, activityCount int64
	DB.Model(&models.Word{}).Count(&wordCount)
	DB.Model(&models.WordGroup{}).Count(&groupCount)
	DB.Model(&models.StudyActivity{}).Count(&activityCount)

	if wordCount == 0 || groupCount == 0 || activityCount == 0 {
		log.Println("Database is empty, loading seed data...")
		if err := SeedDB(DB); err != nil {
			log.Printf("Warning: Failed to load seed data: %v", err)
			return err
		}
	} else {
		log.Printf("Database already contains data: %d words, %d groups, %d activities",
			wordCount, groupCount, activityCount)
	}

	log.Println("Database initialized successfully")
	return nil
}

// GetDB returns the database instance
func GetDB() *gorm.DB {
	return DB
}
