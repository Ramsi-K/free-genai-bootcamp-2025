package handlers

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/Ramsi-K/free-genai-bootcamp-2025/tree/main/projects/lang-portal/backend-go/internal/models"
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
	db, err := setupTestDB(t, nil)
	if err != nil {
		return nil, err
	}

	router := setupTestRouter(db)
	th := &testHelper{db: db, router: router}
	if err := th.seedTestData(); err != nil {
		return nil, err
	}
	return th, nil
}

func setupTestDB(t *testing.T, seedWords []models.Word) (*gorm.DB, error) {
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
		&models.WordsGroups{},
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
			WordGroups: []string{"School", "Education"},
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
			WordGroups: []string{"Food", "Fruits"},
		},
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
		// Word routes
		api.GET("/words", wordHandler.List)
		api.GET("/words/:id", wordHandler.Get)

		// Group routes
		api.GET("/groups", groupHandler.List)
		api.GET("/groups/:id", groupHandler.Get)
		api.GET("/groups/:id/words", groupHandler.GetWords)
		api.GET("/groups/:id/study_sessions", groupHandler.GetStudySessions)

		// Study activity routes
		api.GET("/study-activities", studyActivityHandler.List)
		api.GET("/study-activities/:id", studyActivityHandler.Get)
		api.POST("/study-activities/:id/launch", studyActivityHandler.Launch)

		// Dashboard route
		api.GET("/dashboard", dashboardHandler.GetDashboard)

		// Settings routes
		api.POST("/settings/reset-history", settingsHandler.ResetHistory)
		api.POST("/settings/full-reset", settingsHandler.FullReset)

		// Sentence practice routes
		api.GET("/sentence-practice", sentencePracticeHandler.GetPracticeSentence)
		api.POST("/sentence-practice/attempt", sentencePracticeHandler.SubmitSentenceAttempt)
		api.GET("/sentence-practice/examples", sentencePracticeHandler.GetSentenceExamples)
		api.GET("/sentence-practice/statistics", sentencePracticeHandler.GetSentenceStatistics)
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
	if err := tx.Session(&gorm.Session{AllowGlobalUpdate: true}).Unscoped().Delete(&models.WordsGroups{}).Error; err != nil {
		tx.Rollback()
		return err
	}
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

	// Seed test words using FirstOrCreate to avoid duplicates
	words := []models.Word{
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

	for _, word := range words {
		var existing models.Word
		if err := tx.Where("hangul = ? AND romanization = ?", word.Hangul, word.Romanization).
			First(&existing).Error; err == gorm.ErrRecordNotFound {
			if err := tx.Create(&word).Error; err != nil {
				tx.Rollback()
				return err
			}
		}
	}

	// Seed test groups using FirstOrCreate to avoid duplicates
	type groupData struct {
		Name       string
		WordsCount int
	}
	groupsData := []groupData{
		{"School-related Words", 2},
		{"Basic Words", 0},
	}

	for _, gd := range groupsData {
		var group models.Group
		if err := tx.Where("name = ?", gd.Name).First(&group).Error; err == gorm.ErrRecordNotFound {
			group = models.Group{Name: gd.Name, WordsCount: gd.WordsCount}
			if err := tx.Create(&group).Error; err != nil {
				tx.Rollback()
				return err
			}
		}
	}

	// Seed test study activities using FirstOrCreate
	activities := []models.StudyActivity{
		{
			Name:         "Flashcards",
			Description:  "Practice words with flashcards",
			Type:         "flashcards",
			ThumbnailURL: "/images/flashcards.png",
		},
		{
			Name:         "Multiple Choice",
			Description:  "Practice with multiple choice questions",
			Type:         "multiple_choice",
			ThumbnailURL: "/images/multiple-choice.png",
		},
	}

	for _, activity := range activities {
		var existAct models.StudyActivity
		if err := tx.Where("name = ?", activity.Name).First(&existAct).Error; err == gorm.ErrRecordNotFound {
			if err := tx.Create(&activity).Error; err != nil {
				tx.Rollback()
				return err
			}
		}
	}

	// Link words to group using INSERT OR IGNORE
	if err := tx.Exec("INSERT OR IGNORE INTO words_groups (word_id, group_id) VALUES (1, 1), (2, 1)").Error; err != nil {
		tx.Rollback()
		return err
	}

	// Removed seeding of test study session to allow tests to create their own study sessions

	// Commit transaction
	return tx.Commit().Error
}
