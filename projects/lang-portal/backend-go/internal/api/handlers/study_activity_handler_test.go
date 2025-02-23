package handlers

import (
	"bytes"
	"encoding/json"
	"fmt"
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

	// Setup test DB with seeded data
	db, err := setupTestDB(t)
	assert.NoError(t, err)
	defer cleanupTestDB(db)

	// Setup router with seeded data
	gin.SetMode(gin.TestMode)
	router := gin.New()
	repo := repository.NewStudyActivityRepository(repository.NewBaseRepository(db))
	handler := NewStudyActivityHandler(repo)

	// Register routes
	router.GET("/api/study_activities", handler.ListActivities)
	router.GET("/api/study_activities/:id", handler.GetActivity)
	router.POST("/api/study_activities", handler.CreateStudySession)
	router.GET("/api/dashboard/last_study_session", handler.GetLastStudySession)
	router.GET("/api/dashboard/study_progress", handler.GetStudyProgress)
	router.GET("/api/dashboard/quick_stats", handler.GetQuickStats)

	tests := []struct {
		name           string
		method         string
		path           string
		body           any
		setupData      func(t *testing.T) map[string]any
		expectedStatus int
		validateBody   func(t *testing.T, body []byte, testData map[string]any)
	}{
		{
			name:   "List Activities",
			method: "GET",
			path:   "/api/study_activities",
			setupData: func(t *testing.T) map[string]any {
				var activity models.StudyActivity
				err := db.First(&activity).Error
				assert.NoError(t, err)
				return map[string]any{
					"activity_id": activity.ID,
				}
			},
			expectedStatus: http.StatusOK,
			validateBody: func(t *testing.T, body []byte, _ map[string]any) {
				var response struct {
					Data []models.StudyActivity `json:"data"`
				}
				assert.NoError(t, json.Unmarshal(body, &response))
				assert.NotEmpty(t, response.Data)
			},
		},
		{
			name:   "Get Activity",
			method: "GET",
			path:   "", // Will be set in test based on activity ID
			setupData: func(t *testing.T) map[string]any {
				var activity models.StudyActivity
				err := db.First(&activity).Error
				assert.NoError(t, err)
				return map[string]any{
					"activity_id": activity.ID,
				}
			},
			expectedStatus: http.StatusOK,
			validateBody: func(t *testing.T, body []byte, data map[string]any) {
				var activity models.StudyActivity
				assert.NoError(t, json.Unmarshal(body, &activity))
				assert.NotZero(t, activity.ID)
			},
		},
		{
			name:   "Create Study Session - Valid Data",
			method: "POST",
			path:   "/api/study_activities",
			setupData: func(t *testing.T) map[string]any {
				var group models.WordGroup
				err := db.First(&group).Error
				assert.NoError(t, err)

				var activity models.StudyActivity
				err = db.First(&activity).Error
				assert.NoError(t, err)

				return map[string]any{
					"group_id":    group.ID,
					"activity_id": activity.ID,
				}
			},
			body: func(data map[string]any) models.StudySession {
				return models.StudySession{
					StudyActivityID: data["activity_id"].(uint),
					WordGroupID:     &[]uint{data["group_id"].(uint)}[0],
					CorrectCount:    8,
					WrongCount:      2,
					CompletedAt:     time.Now(),
				}
			},
			expectedStatus: http.StatusCreated,
			validateBody: func(t *testing.T, body []byte, testData map[string]any) {
				var response map[string]any
				err := json.Unmarshal(body, &response)
				assert.NoError(t, err)
				assert.NotNil(t, response["id"])
				assert.Equal(t, float64(testData["group_id"].(uint)), response["group_id"])
				assert.Equal(t, float64(testData["activity_id"].(uint)), response["activity_id"])
			},
		},
		{
			name:   "Create Study Session - Invalid Activity ID",
			method: "POST",
			path:   "/api/study_activities",
			setupData: func(t *testing.T) map[string]any {
				var group models.WordGroup
				err := db.First(&group).Error
				assert.NoError(t, err)
				return map[string]any{
					"group_id": group.ID,
				}
			},
			body: func(data map[string]any) models.StudySession {
				return models.StudySession{
					StudyActivityID: 999, // Non-existent activity
					WordGroupID:     &[]uint{data["group_id"].(uint)}[0],
					CorrectCount:    8,
					WrongCount:      2,
					CompletedAt:     time.Now(),
				}
			},
			expectedStatus: http.StatusNotFound,
		},
		{
			name:   "Create Study Session - Invalid Group ID",
			method: "POST",
			path:   "/api/study_activities",
			setupData: func(t *testing.T) map[string]any {
				var activity models.StudyActivity
				err := db.First(&activity).Error
				assert.NoError(t, err)
				return map[string]any{
					"activity_id": activity.ID,
				}
			},
			body: func(data map[string]any) models.StudySession {
				invalidID := uint(999)
				return models.StudySession{
					StudyActivityID: data["activity_id"].(uint),
					WordGroupID:     &invalidID,
					CorrectCount:    8,
					WrongCount:      2,
					CompletedAt:     time.Now(),
				}
			},
			expectedStatus: http.StatusNotFound,
		},
		{
			name:           "Create Study Session - Invalid Request Body",
			method:         "POST",
			path:           "/api/study_activities",
			body:           "invalid json",
			expectedStatus: http.StatusBadRequest,
			setupData: func(t *testing.T) map[string]any {
				return nil
			},
		},
		{
			name:   "Get Last Study Session",
			method: "GET",
			path:   "/api/dashboard/last_study_session",
			setupData: func(t *testing.T) map[string]any {
				// Create multiple study sessions using seeded data
				var group models.WordGroup
				var activity models.StudyActivity
				err := db.First(&group).Error
				assert.NoError(t, err)
				err = db.First(&activity).Error
				assert.NoError(t, err)

				// Create 3 study sessions
				for i := 0; i < 3; i++ {
					session := models.StudySession{
						WordGroupID:     &group.ID,
						StudyActivityID: activity.ID,
						CorrectCount:    int(i + 1),
						WrongCount:      int(i),
						CompletedAt:     time.Now(),
					}
					err := db.Create(&session).Error
					assert.NoError(t, err)
				}
				return map[string]any{}
			},
			expectedStatus: http.StatusOK,
			validateBody: func(t *testing.T, body []byte, _ map[string]any) {
				var response map[string]any
				err := json.Unmarshal(body, &response)
				assert.NoError(t, err)
				// Basic validation of response structure
				assert.NotNil(t, response["id"])
				assert.NotNil(t, response["group_id"])
				assert.NotNil(t, response["activity_id"])
				assert.NotNil(t, response["completed_at"])
			},
		},
		{
			name:   "Get Study Progress",
			method: "GET",
			path:   "/api/dashboard/study_progress",
			setupData: func(t *testing.T) map[string]any {
				// Use existing seeded word
				var word models.Word
				err := db.First(&word).Error
				assert.NoError(t, err)
				return map[string]any{
					"word_id": word.ID,
				}
			},
			expectedStatus: http.StatusOK,
			validateBody: func(t *testing.T, body []byte, _ map[string]any) {
				var progress map[string]any
				assert.NoError(t, json.Unmarshal(body, &progress))
				// Basic validation of response structure
				assert.Contains(t, progress, "total_words")
				assert.Contains(t, progress, "studied_words")
			},
		},
		{
			name:   "Get Quick Stats",
			method: "GET",
			path:   "/api/dashboard/quick_stats",
			setupData: func(t *testing.T) map[string]any {
				return nil // No setup needed
			},
			expectedStatus: http.StatusOK,
			validateBody: func(t *testing.T, body []byte, _ map[string]any) {
				var stats map[string]any
				assert.NoError(t, json.Unmarshal(body, &stats))
				// Basic validation of response structure
				assert.Contains(t, stats, "total_sessions")
				assert.Contains(t, stats, "active_groups")
				assert.Contains(t, stats, "success_rate")
			},
		},
	}

	// Run test cases
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Reset database before each test
			if err := resetTestDB(db); err != nil {
				t.Fatalf("Failed to reset database: %v", err)
			}

			// Setup test data
			var testData map[string]any
			if tt.setupData != nil {
				testData = tt.setupData(t)
			}

			// Update path for Get Activity test
			if tt.name == "Get Activity" {
				if id, ok := testData["activity_id"].(uint); ok {
					tt.path = fmt.Sprintf("/api/study_activities/%d", id)
				}
			}

			// Prepare request
			var req *http.Request
			if tt.body != nil {
				var bodyBytes []byte
				var err error
				// If the body is provided as a function, call it with testData
				if bodyFn, ok := tt.body.(func(map[string]any) models.StudySession); ok && testData != nil {
					bodyObj := bodyFn(testData)
					bodyBytes, err = json.Marshal(bodyObj)
					if err != nil {
						t.Fatalf("Failed to marshal body: %v", err)
					}
				} else {
					bodyBytes, err = json.Marshal(tt.body)
					if err != nil {
						t.Fatalf("Failed to marshal body: %v", err)
					}
				}
				req = httptest.NewRequest(tt.method, tt.path, bytes.NewBuffer(bodyBytes))
				req.Header.Set("Content-Type", "application/json")
			} else {
				req = httptest.NewRequest(tt.method, tt.path, nil)
			}

			// Perform request
			w := httptest.NewRecorder()
			router.ServeHTTP(w, req)

			// Validate response status and body
			assert.Equal(t, tt.expectedStatus, w.Code, fmt.Sprintf("Expected status %d but got %d: %s", tt.expectedStatus, w.Code, w.Body.String()))
			if tt.validateBody != nil && w.Code == tt.expectedStatus && w.Code < 400 {
				tt.validateBody(t, w.Body.Bytes(), testData)
			}
		})
	}
}
