package database

import (
	"fmt"
	"os"
	"path/filepath"

	"github.com/Ramsi-K/free-genai-bootcamp-2025/projects/lang-portal/backend-go/internal/models"

	_ "github.com/mattn/go-sqlite3" // SQLite driver
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

// SetupDB initializes the database connection and runs migrations
func SetupDB() (*gorm.DB, error) {
	// Ensure instance directory exists
	if err := os.MkdirAll("instance", 0755); err != nil {
		return nil, fmt.Errorf("failed to create instance directory: %v", err)
	}

	dbPath := filepath.Join("instance", "words.db")

	// Configure GORM with SQLite
	config := &gorm.Config{
		Logger:                                   logger.Default.LogMode(logger.Info),
		DisableForeignKeyConstraintWhenMigrating: true, // SQLite specific
	}

	db, err := gorm.Open(sqlite.Open(dbPath+"?_fk=1"), config)
	if err != nil {
		return nil, fmt.Errorf("failed to connect to database: %v", err)
	}

	// Set connection pool settings
	sqlDB, err := db.DB()
	if err != nil {
		return nil, fmt.Errorf("failed to get database instance: %v", err)
	}

	// Set connection pool settings
	sqlDB.SetMaxIdleConns(10)
	sqlDB.SetMaxOpenConns(100)

	// Run migrations immediately
	if err := MigrateDB(db); err != nil {
		return nil, fmt.Errorf("failed to run migrations: %v", err)
	}

	// Verify database schema
	if err := VerifyDB(db); err != nil {
		return nil, fmt.Errorf("database verification failed: %v", err)
	}

	return db, nil
}

// MigrateDB runs all database migrations
func MigrateDB(db *gorm.DB) error {
	// Auto Migrate the schema
	if err := db.AutoMigrate(
		&models.Word{},
		&models.Group{},
		&models.StudySession{},
		&models.StudyActivity{},
		&models.WordReview{},
		&models.SentencePracticeAttempt{},
	); err != nil {
		return fmt.Errorf("failed to migrate database: %v", err)
	}

	return nil
}

// VerifyDB checks if all required tables exist
func VerifyDB(db *gorm.DB) error {
	// List of required tables
	requiredTables := []string{
		"words",
		"groups",
		"study_sessions",
		"study_activities",
		"word_reviews",
		"sentence_practice_attempts",
	}

	// Get list of existing tables
	var tables []string
	if err := db.Raw("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").Pluck("name", &tables).Error; err != nil {
		return fmt.Errorf("failed to get table list: %v", err)
	}

	// Create a map for easy lookup
	tableMap := make(map[string]bool)
	for _, table := range tables {
		tableMap[table] = true
	}

	// Check if all required tables exist
	missingTables := []string{}
	for _, table := range requiredTables {
		if !tableMap[table] {
			missingTables = append(missingTables, table)
		}
	}

	if len(missingTables) > 0 {
		return fmt.Errorf("missing required tables: %v", missingTables)
	}

	return nil
}

// InitDB initializes a new database with schema
func InitDB(dbPath string) (*gorm.DB, error) {
	config := &gorm.Config{
		Logger:                                   logger.Default.LogMode(logger.Info),
		DisableForeignKeyConstraintWhenMigrating: true,
	}

	db, err := gorm.Open(sqlite.Open(dbPath+"?_fk=1"), config)
	if err != nil {
		return nil, fmt.Errorf("failed to connect to database: %v", err)
	}

	// Run migrations
	if err := MigrateDB(db); err != nil {
		return nil, fmt.Errorf("failed to run migrations: %v", err)
	}

	// Verify database schema
	if err := VerifyDB(db); err != nil {
		return nil, fmt.Errorf("database verification failed: %v", err)
	}

	return db, nil
}
