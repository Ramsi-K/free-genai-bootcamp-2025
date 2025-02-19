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

func TestStudyActivityHandler_Integration(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test")
	}

	// Setup
	db, err := setupTestDB()
	if err != nil {
		t.Fatalf("Failed to setup test database: %v", err)
	}

	// Setup router
	gin.SetMode(gin.TestMode)
	router := gin.New()
	repo := repository.NewStudyActivityRepository(repository.NewBaseRepository(db))
	handler := NewStudyActivityHandler(repo)

	router.GET("/api/study_activities", handler.ListActivities)
	router.GET("/api/study_activities/:id", handler.GetActivity)
	router.POST("/api/study_activities", handler.CreateStudySession)
	router.GET("/api/dashboard/last_study_session", handler.GetLastStudySession)
	router.GET("/api/dashboard/study_progress", handler.GetStudyProgress)
	router.GET("/api/dashboard/quick_stats", handler.GetQuickStats)

	// Test cases
	tests := []struct {
		name           string
		method         string
		path           string
		body           interface{}
		setupData      func(t *testing.T) (*models.WordGroup, *models.StudyActivity, *models.StudySession)
		expectedStatus int
		validateBody   func(t *testing.T, body []byte, testData map[string]interface{})
	}{
		{
			name:   "Create Study Session",
			method: "POST",
			path:   "/api/study_activities",
			setupData: func(t *testing.T) (*models.WordGroup, *models.StudyActivity, *models.StudySession) {
				group, err := createTestGroup(db, "Test Group", nil)
				if err != nil {
					t.Fatalf("Failed to create test group: %v", err)
				}

				activity, err := createTestActivity(db, "Test Activity")
				if err != nil {
					t.Fatalf("Failed to create test activity: %v", err)
				}

				return group, activity, nil
			},
			body: models.StudySession{
				GroupID:      1, // Will be replaced with actual ID
				ActivityID:   1, // Will be replaced with actual ID
				CorrectCount: 8,
				WrongCount:   2,
				CompletedAt:  time.Now(),
			},
			expectedStatus: http.StatusCreated,
			validateBody: func(t *testing.T, body []byte, testData map[string]interface{}) {
				var response struct {
					ID           uint      `json:"id"`
					GroupID      uint      `json:"group_id"`
					ActivityID   uint      `json:"activity_id"`
					CorrectCount uint      `json:"correct_count"`
					WrongCount   uint      `json:"wrong_count"`
					CompletedAt  time.Time `json:"completed_at"`
				}
				assert.NoError(t, json.Unmarshal(body, &response))
				assert.Equal(t, uint(8), response.CorrectCount)
				assert.Equal(t, uint(2), response.WrongCount)
				assert.Equal(t, testData["group_id"].(uint), response.GroupID)
				assert.Equal(t, testData["activity_id"].(uint), response.ActivityID)
			},
		},
		{
			name:           "List Activities",
			method:         "GET",
			path:           "/api/study_activities",
			expectedStatus: http.StatusOK,
			validateBody: func(t *testing.T, body []byte, _ map[string]interface{}) {
				var response struct {
					Data []models.StudyActivity `json:"data"`
				}
				assert.NoError(t, json.Unmarshal(body, &response))
				assert.Len(t, response.Data, 1)
				assert.Equal(t, "Test Activity", response.Data[0].Name)
			},
		},
		{
			name:           "Get Activity",
			method:         "GET",
			path:           "/api/study_activities/1",
			expectedStatus: http.StatusOK,
			validateBody: func(t *testing.T, body []byte, _ map[string]interface{}) {
				var activity models.StudyActivity
				assert.NoError(t, json.Unmarshal(body, &activity))
				assert.Equal(t, "Test Activity", activity.Name)
			},
		},
		{
			name:   "Create Study Session - Invalid Activity ID",
			method: "POST",
			path:   "/api/study_activities",
			setupData: func(t *testing.T) (*models.WordGroup, *models.StudyActivity, *models.StudySession) {
				group, err := createTestGroup(db, "Test Group", nil)
				if err != nil {
					t.Fatalf("Failed to create test group: %v", err)
				}
				return group, nil, nil
			},
			body: models.StudySession{
				GroupID:      1,   // Will be replaced with actual ID
				ActivityID:   999, // Non-existent activity
				CorrectCount: 8,
				WrongCount:   2,
				CompletedAt:  time.Now(),
			},
			expectedStatus: http.StatusNotFound,
		},
		{
			name:   "Create Study Session - Invalid Group ID",
			method: "POST",
			path:   "/api/study_activities",
			setupData: func(t *testing.T) (*models.WordGroup, *models.StudyActivity, *models.StudySession) {
				activity, err := createTestActivity(db, "Test Activity")
				if err != nil {
					t.Fatalf("Failed to create test activity: %v", err)
				}
				return nil, activity, nil
			},
			body: models.StudySession{
				GroupID:      999, // Non-existent group
				ActivityID:   1,   // Will be replaced with actual ID
				CorrectCount: 8,
				WrongCount:   2,
				CompletedAt:  time.Now(),
			},
			expectedStatus: http.StatusNotFound,
		},
		{
			name:           "Create Study Session - Invalid Request Body",
			method:         "POST",
			path:           "/api/study_activities",
			body:           "invalid json",
			expectedStatus: http.StatusBadRequest,
		},
		{
			name:   "Get Last Study Session",
			method: "GET",
			path:   "/api/dashboard/last_study_session",
			setupData: func(t *testing.T) (*models.WordGroup, *models.StudyActivity, *models.StudySession) {
				group, err := createTestGroup(db, "Test Group", nil)
				if err != nil {
					t.Fatalf("Failed to create test group: %v", err)
				}

				activity, err := createTestActivity(db, "Test Activity")
				if err != nil {
					t.Fatalf("Failed to create test activity: %v", err)
				}

				session, err := createTestStudySession(db, group.ID, activity.ID)
				if err != nil {
					t.Fatalf("Failed to create test session: %v", err)
				}

				return group, activity, session
			},
			expectedStatus: http.StatusOK,
			validateBody: func(t *testing.T, body []byte, testData map[string]interface{}) {
				var response struct {
					ID           uint      `json:"id"`
					GroupID      uint      `json:"group_id"`
					ActivityID   uint      `json:"activity_id"`
					CorrectCount uint      `json:"correct_count"`
					WrongCount   uint      `json:"wrong_count"`
					CompletedAt  time.Time `json:"completed_at"`
				}
				assert.NoError(t, json.Unmarshal(body, &response))
				assert.Equal(t, testData["group_id"].(uint), response.GroupID)
				assert.Equal(t, testData["activity_id"].(uint), response.ActivityID)
				assert.Equal(t, uint(5), response.CorrectCount) // From createTestStudySession
				assert.Equal(t, uint(2), response.WrongCount)   // From createTestStudySession
			},
		},
		{
			name:           "Get Study Progress",
			method:         "GET",
			path:           "/api/dashboard/study_progress",
			expectedStatus: http.StatusOK,
			validateBody: func(t *testing.T, body []byte, _ map[string]interface{}) {
				var progress map[string]interface{}
				assert.NoError(t, json.Unmarshal(body, &progress))
				assert.Contains(t, progress, "total_words")
				assert.Contains(t, progress, "studied_words")
				assert.Contains(t, progress, "success_rate")
			},
		},
		{
			name:           "Get Quick Stats",
			method:         "GET",
			path:           "/api/dashboard/quick_stats",
			expectedStatus: http.StatusOK,
			validateBody: func(t *testing.T, body []byte, _ map[string]interface{}) {
				var stats map[string]interface{}
				assert.NoError(t, json.Unmarshal(body, &stats))
				assert.Contains(t, stats, "total_sessions")
				assert.Contains(t, stats, "active_groups")
				assert.Contains(t, stats, "success_rate")
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			withCleanDB(t, db, func() {
				var testData = make(map[string]interface{})

				// Setup test data
				if tt.setupData != nil {
					group, activity, session := tt.setupData(t)
					testData["group_id"] = group.ID
					testData["activity_id"] = activity.ID
					if session != nil {
						testData["session_id"] = session.ID
					}

					// Update request body with actual IDs if it's a StudySession
					if sessionBody, ok := tt.body.(models.StudySession); ok {
						sessionBody.GroupID = group.ID
						sessionBody.ActivityID = activity.ID
						tt.body = sessionBody
					}
				}

				var req *http.Request
				if tt.body != nil {
					bodyBytes, _ := json.Marshal(tt.body)
					req = httptest.NewRequest(tt.method, tt.path, bytes.NewBuffer(bodyBytes))
					req.Header.Set("Content-Type", "application/json")
				} else {
					req = httptest.NewRequest(tt.method, tt.path, nil)
				}

				w := httptest.NewRecorder()
				router.ServeHTTP(w, req)

				assert.Equal(t, tt.expectedStatus, w.Code)
				if tt.validateBody != nil && w.Code == tt.expectedStatus {
					tt.validateBody(t, w.Body.Bytes(), testData)
				}
			})
		})
	}
}
