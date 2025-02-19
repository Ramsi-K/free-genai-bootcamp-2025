package handlers

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/Ramsi-K/free-genai-bootcamp-2025/tree/main/projects/lang-portal/backend-go/internal/models"
	"github.com/gin-gonic/gin"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
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
	return &testHelper{db: db, router: router}, nil
}

func setupTestDB(t *testing.T, seedWords []models.Word) (*gorm.DB, error) {
	db, err := gorm.Open(sqlite.Open(":memory:"), &gorm.Config{})
	if err != nil {
		return nil, err
	}

	// Auto migrate the schema
	err = db.AutoMigrate(&models.Word{}, &models.Group{}, &models.StudyActivity{}, &models.StudySession{}, &models.WordReview{}, &models.WordsGroups{})
	if err != nil {
		return nil, err
	}

	// If seed words are provided, insert them
	if len(seedWords) > 0 {
		for _, word := range seedWords {
			if err := db.Create(&word).Error; err != nil {
				return nil, err
			}
		}
	}

	return db, nil
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

	// Register routes
	r.GET("/api/words", wordHandler.List)
	r.GET("/api/words/:id", wordHandler.Get)
	r.GET("/api/groups", groupHandler.List)
	r.GET("/api/groups/:id", groupHandler.Get)
	r.GET("/api/groups/:id/words", groupHandler.GetWords)
	r.GET("/api/study-activities", studyActivityHandler.List)
	r.GET("/api/study-activities/:id", studyActivityHandler.Get)
	r.POST("/api/study-activities/:id/launch", studyActivityHandler.Launch)
	r.GET("/api/dashboard", dashboardHandler.GetDashboard)
	r.POST("/api/settings/reset-history", settingsHandler.ResetHistory)
	r.POST("/api/settings/full-reset", settingsHandler.FullReset)

	return r
}

func getTestWords() []models.Word {
	return []models.Word{
		{
			Hangul:       "학교",
			Romanization: "hakgyo",
			English:      []string{"school"},
			Type:         "noun",
			Example: models.Example{
				Korean:  "나는 학교에 갑니다",
				English: "I go to school",
			},
		},
		{
			Hangul:       "사과",
			Romanization: "sagwa",
			English:      []string{"apple"},
			Type:         "noun",
			Example: models.Example{
				Korean:  "사과를 먹습니다",
				English: "I eat an apple",
			},
		},
	}
}

func (h *testHelper) seedTestData() error {
	// Create test words
	testWords := getTestWords()
	for _, word := range testWords {
		if err := h.db.Create(&word).Error; err != nil {
			return err
		}
	}

	// Create test groups
	groups := []models.Group{
		{
			Name:       "School-related Words",
			WordsCount: 2,
		},
		{
			Name:       "Basic Words",
			WordsCount: 0,
		},
	}

	for _, group := range groups {
		if err := h.db.Create(&group).Error; err != nil {
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
			Description:  "Practice with multiple choice questions",
			Type:         "multiple_choice",
			ThumbnailURL: "/images/multiple-choice.png",
		},
	}

	for _, activity := range activities {
		if err := h.db.Create(&activity).Error; err != nil {
			return err
		}
	}

	// Create test study session
	now := time.Now()
	session := models.StudySession{
		GroupID:         1,
		StudyActivityID: 1,
		CompletedAt:     &now,
	}

	if err := h.db.Create(&session).Error; err != nil {
		return err
	}

	// Create test word reviews
	reviews := []models.WordReview{
		{
			WordID:         1,
			StudySessionID: 1,
			Correct:        true,
		},
		{
			WordID:         2,
			StudySessionID: 1,
			Correct:        false,
		},
	}

	for _, review := range reviews {
		if err := h.db.Create(&review).Error; err != nil {
			return err
		}
	}

	// Link words to groups
	if err := h.db.Exec("INSERT INTO words_groups (word_id, group_id) VALUES (1, 1), (2, 1)").Error; err != nil {
		return err
	}

	return nil
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
