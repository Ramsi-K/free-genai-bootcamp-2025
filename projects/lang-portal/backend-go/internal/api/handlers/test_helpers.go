package handlers

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
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
	tmpDir string
}

func newTestHelper(t *testing.T) (*testHelper, error) {
	// Create a temporary directory for test data
	tmpDir, err := os.MkdirTemp("", "lang-portal-test-*")
	if err != nil {
		return nil, err
	}

	// Create seed directory
	seedDir := filepath.Join(tmpDir, "seed")
	if err := os.MkdirAll(seedDir, 0755); err != nil {
		os.RemoveAll(tmpDir)
		return nil, err
	}

	// Create test word_groups.json
	wordGroups := []map[string]interface{}{
		{
			"hangul":      "학교",
			"group_names": []string{"School", "Education", "Basic Words"},
		},
		{
			"hangul":      "사과",
			"group_names": []string{"Food", "Fruits", "Basic Words"},
		},
	}

	wordGroupsData, err := json.Marshal(wordGroups)
	if err != nil {
		os.RemoveAll(tmpDir)
		return nil, err
	}

	if err := os.WriteFile(filepath.Join(seedDir, "word_groups.json"), wordGroupsData, 0644); err != nil {
		os.RemoveAll(tmpDir)
		return nil, err
	}

	// Set up database
	db, err := setupTestDB(t)
	if err != nil {
		os.RemoveAll(tmpDir)
		return nil, err
	}

	// Set up router
	router := setupTestRouter(db)

	return &testHelper{
		db:     db,
		router: router,
		tmpDir: tmpDir,
	}, nil
}

func (h *testHelper) Cleanup() {
	if h.tmpDir != "" {
		os.RemoveAll(h.tmpDir)
	}
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
	// Create test words
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

	// Insert words into database
	for _, word := range words {
		if err := h.db.Create(&word).Error; err != nil {
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
	}

	for _, activity := range activities {
		if err := h.db.Create(&activity).Error; err != nil {
			return err
		}
	}

	return nil
}
