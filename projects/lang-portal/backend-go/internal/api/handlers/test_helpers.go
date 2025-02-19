package handlers

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/Ramsi-K/free-genai-bootcamp-2025/projects/lang-portal/backend-go/internal/models"
	"github.com/gin-gonic/gin"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

type testHelper struct {
	db     *gorm.DB
	router *gin.Engine
}

func newTestHelper(t *testing.T) (*testHelper, error) {
	db, err := setupTestDB(t)
	if err != nil {
		return nil, err
	}

	router := setupTestRouter(db)
	return &testHelper{db: db, router: router}, nil
}

func setupTestDB(t *testing.T) (*gorm.DB, error) {
	db, err := gorm.Open(sqlite.Open(":memory:"), &gorm.Config{
		Logger: logger.Default.LogMode(logger.Silent),
	})
	if err != nil {
		return nil, err
	}

	// Run migrations
	err = db.AutoMigrate(
		&models.Word{},
		&models.Group{},
		&models.StudyActivity{},
		&models.StudySession{},
		&models.WordReview{},
		&models.SentencePracticeAttempt{},
	)
	if err != nil {
		return nil, err
	}

	return db, nil
}

func getTestWords() []models.Word {
	return []models.Word{
		{
			Hangul:       "학교",
			Romanization: "hakgyo",
			English:      []string{"school"},
			Type:         "noun",
			ExampleSentence: models.Example{
				Korean:  "나는 학교에 갑니다",
				English: "I go to school",
			},
		},
		{
			Hangul:       "사과",
			Romanization: "sagwa",
			English:      []string{"apple"},
			Type:         "noun",
			ExampleSentence: models.Example{
				Korean:  "사과를 먹습니다",
				English: "I eat an apple",
			},
		},
	}
}

func getTestGroups() []models.Group {
	return []models.Group{
		{Name: "School", WordsCount: 1},
		{Name: "Food", WordsCount: 1},
		{Name: "Basic Words", WordsCount: 2},
	}
}

func setupTestRouter(db *gorm.DB) *gin.Engine {
	gin.SetMode(gin.TestMode)
	r := gin.New()

	// Add handlers
	wordHandler := NewWordHandler(db)
	groupHandler := NewGroupHandler(db)
	studyActivityHandler := NewStudyActivityHandler(db)
	dashboardHandler := NewDashboardHandler(db)
	settingsHandler := NewSettingsHandler(db)
	sentencePracticeHandler := NewSentencePracticeHandler(db)

	// Register routes
	api := r.Group("/api")
	{
		// Dashboard routes
		api.GET("/dashboard", dashboardHandler.GetDashboard)
		api.GET("/dashboard/last_study_session", dashboardHandler.GetLastStudySession)
		api.GET("/dashboard/study_progress", dashboardHandler.GetStudyProgress)
		api.GET("/dashboard/quick_stats", dashboardHandler.GetQuickStats)

		// Word routes
		api.GET("/words", wordHandler.List)
		api.GET("/words/:id", wordHandler.Get)

		// Group routes
		api.GET("/groups", groupHandler.List)
		api.GET("/groups/:id", groupHandler.Get)
		api.GET("/groups/:id/words", groupHandler.GetWords)
		api.GET("/groups/:id/study_sessions", groupHandler.GetStudySessions)

		// Study activity routes
		api.GET("/study_activities", studyActivityHandler.List)
		api.GET("/study_activities/:id", studyActivityHandler.Get)
		api.GET("/study_activities/:id/study_sessions", studyActivityHandler.GetSessions)
		api.POST("/study_activities/:id/launch", studyActivityHandler.Launch)

		// Settings routes
		api.POST("/settings/reset_history", settingsHandler.ResetHistory)
		api.POST("/settings/full_reset", settingsHandler.FullReset)

		// Sentence practice routes
		api.GET("/sentence_practice", sentencePracticeHandler.GetPracticeSentence)
		api.POST("/sentence_practice/attempt", sentencePracticeHandler.SubmitSentenceAttempt)
		api.GET("/sentence_practice/examples", sentencePracticeHandler.GetSentenceExamples)
		api.GET("/sentence_practice/statistics", sentencePracticeHandler.GetSentenceStatistics)
	}

	return r
}

func performRequest(r http.Handler, method, path string, body interface{}) *httptest.ResponseRecorder {
	var reqBody []byte
	if body != nil {
		reqBody, _ = json.Marshal(body)
	}
	req := httptest.NewRequest(method, path, bytes.NewBuffer(reqBody))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)
	return w
}

func parseResponse(w *httptest.ResponseRecorder) (map[string]interface{}, error) {
	var response map[string]interface{}
	err := json.Unmarshal(w.Body.Bytes(), &response)
	return response, err
}

func parseWordList(w *httptest.ResponseRecorder) ([]map[string]interface{}, error) {
	var response []map[string]interface{}
	err := json.Unmarshal(w.Body.Bytes(), &response)
	return response, err
}

func (h *testHelper) seedTestData() error {
	// Begin transaction
	tx := h.db.Begin()
	if tx.Error != nil {
		return tx.Error
	}

	// Clean up tables to prevent duplicate seed data using Unscoped() to permanently delete rows
	if err := tx.Session(&gorm.Session{AllowGlobalUpdate: true}).Unscoped().Delete(&models.Word{}).Error; err != nil {
		tx.Rollback()
		return err
	}
	if err := tx.Session(&gorm.Session{AllowGlobalUpdate: true}).Unscoped().Delete(&models.Group{}).Error; err != nil {
		tx.Rollback()
		return err
	}
	if err := tx.Session(&gorm.Session{AllowGlobalUpdate: true}).Unscoped().Delete(&models.StudyActivity{}).Error; err != nil {
		tx.Rollback()
		return err
	}
	if err := tx.Session(&gorm.Session{AllowGlobalUpdate: true}).Unscoped().Delete(&models.StudySession{}).Error; err != nil {
		tx.Rollback()
		return err
	}
	if err := tx.Session(&gorm.Session{AllowGlobalUpdate: true}).Unscoped().Delete(&models.SentencePracticeAttempt{}).Error; err != nil {
		tx.Rollback()
		return err
	}

	// Create test words
	words := getTestWords()
	for _, word := range words {
		if err := tx.Create(&word).Error; err != nil {
			tx.Rollback()
			return err
		}
	}

	// Create test groups
	groups := getTestGroups()
	for _, group := range groups {
		if err := tx.Create(&group).Error; err != nil {
			tx.Rollback()
			return err
		}
	}

	// Create test study activities
	activities := []models.StudyActivity{
		{
			Name:         "Flashcards",
			Description:  "Practice words with flashcards",
			Type:         "flashcards",
			ThumbnailURL: "/images/flashcards.png",
		},
		{
			Name:         "Multiple Choice",
			Description:  "Test your knowledge with multiple choice questions",
			Type:         "multiple_choice",
			ThumbnailURL: "/images/multiple_choice.png",
		},
		{
			Name:         "Sentence Practice",
			Description:  "Practice using words in sentences",
			Type:         "sentence_practice",
			ThumbnailURL: "/images/sentence_practice.png",
		},
	}

	for _, activity := range activities {
		if err := tx.Create(&activity).Error; err != nil {
			tx.Rollback()
			return err
		}
	}

	return tx.Commit().Error
}
