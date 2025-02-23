package handlers

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/models"
	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/repository"
	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
)

func uintPtr(i uint) *uint {
	return &i
}

func TestStudySession_Integration(t *testing.T) {
	// Setup
	db, err := setupTestDB(t)
	assert.NoError(t, err)
	defer cleanupTestDB(db)

	// Setup router
	gin.SetMode(gin.TestMode)
	router := gin.New()
	activityRepo := repository.NewStudyActivityRepository(repository.NewBaseRepository(db))
	handler := NewStudyActivityHandler(activityRepo)

	// Register routes
	router.POST("/api/study/sessions", handler.CreateStudySession)

	// Test creating a study session
	session := models.StudySession{
		WordGroupID:     uintPtr(1), // Use ID from test word groups
		StudyActivityID: 1,          // Use ID from test study activities
		CorrectCount:    5,
		WrongCount:      2,
		CompletedAt:     time.Now(),
	}

	reqBody, err := json.Marshal(session)
	assert.NoError(t, err)

	req := httptest.NewRequest("POST", "/api/study/sessions", bytes.NewBuffer(reqBody))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusCreated, w.Code)

	// Verify session was created
	var createdSession struct {
		ID           uint      `json:"id"`
		GroupID      uint      `json:"group_id"`
		ActivityID   uint      `json:"activity_id"`
		CorrectCount uint      `json:"correct_count"`
		WrongCount   uint      `json:"wrong_count"`
		CompletedAt  time.Time `json:"completed_at"`
	}

	err = json.Unmarshal(w.Body.Bytes(), &createdSession)
	assert.NoError(t, err)
	assert.Equal(t, session.WordGroupID, createdSession.GroupID)
	assert.Equal(t, session.StudyActivityID, createdSession.ActivityID)
}
