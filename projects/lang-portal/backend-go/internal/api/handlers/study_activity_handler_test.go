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

	// Setup
	db, err := setupTestDB()
	if err != nil {
		t.Fatalf("Failed to setup test database: %v", err)
	}
	defer cleanupTestDB(db)

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
		setupData      func(t *testing.T) map[string]interface{}
		expectedStatus int
		validateBody   func(t *testing.T, body []byte, testData map[string]interface{})
	}{
		{
			name:   "List Activities",
			method: "GET",
			path:   "/api/study_activities",
			setupData: func(t *testing.T) map[string]interface{} {
				activity, err := createTestActivity(db, "Test Activity")
				if err != nil {
					t.Fatalf("Failed to create test activity: %v", err)
				}
				return map[string]interface{}{
					"activity_id": activity.ID,
				}
			},
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
			name:   "Get Activity",
			method: "GET",
			path:   "/api/study_activities/1",
			setupData: func(t *testing.T) map[string]interface{} {
				activity, err := createTestActivity(db, "Test Activity")
				if err != nil {
					t.Fatalf("Failed to create test activity: %v", err)
				}
				return map[string]interface{}{
					"activity_id": activity.ID,
				}
			},
			expectedStatus: http.StatusOK,
			validateBody: func(t *testing.T, body []byte, _ map[string]interface{}) {
				var activity models.StudyActivity
				assert.NoError(t, json.Unmarshal(body, &activity))
				assert.Equal(t, "Test Activity", activity.Name)
			},
		},
		{
			name:   "Create Study Session - Valid Data",
			method: "POST",
			path:   "/api/study_activities",
			setupData: func(t *testing.T) map[string]interface{} {
				// Create a group
				group, err := createTestGroup(db, "Test Group", nil)
				if err != nil {
					t.Fatalf("Failed to create test group: %v", err)
				}

				// Create an activity
				activity, err := createTestActivity(db, "Test Activity")
				if err != nil {
					t.Fatalf("Failed to create test activity: %v", err)
				}

				return map[string]interface{}{
					"group_id":    group.ID,
					"activity_id": activity.ID,
				}
			},
			body: func(data map[string]interface{}) models.StudySession {
				return models.StudySession{
					StudyActivityID: data["activity_id"].(uint),
					WordGroupID:     &[]uint{data["group_id"].(uint)}[0],
					CorrectCount:    8,
					WrongCount:      2,
					CompletedAt:     time.Now(),
				}
			},
			expectedStatus: http.StatusCreated,
			validateBody: func(t *testing.T, body []byte, testData map[string]interface{}) {
				var response map[string]interface{}
				err := json.Unmarshal(body, &response)
				assert.NoError(t, err)

				// Verify fields
				assert.NotNil(t, response["id"])
				assert.Equal(t, float64(testData["group_id"].(uint)), response["group_id"])
				assert.Equal(t, float64(testData["activity_id"].(uint)), response["activity_id"])
				assert.Equal(t, float64(8), response["correct_count"])
				assert.Equal(t, float64(2), response["wrong_count"])
				assert.NotNil(t, response["completed_at"])
				assert.NotNil(t, response["created_at"])
				assert.NotNil(t, response["updated_at"])
			},
		},
		{
			name:   "Create Study Session - Invalid Activity ID",
			method: "POST",
			path:   "/api/study_activities",
			setupData: func(t *testing.T) map[string]interface{} {
				group, err := createTestGroup(db, "Test Group", nil)
				if err != nil {
					t.Fatalf("Failed to create test group: %v", err)
				}
				return map[string]interface{}{
					"group_id": group.ID,
				}
			},
			body: func(data map[string]interface{}) models.StudySession {
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
			setupData: func(t *testing.T) map[string]interface{} {
				activity, err := createTestActivity(db, "Test Activity")
				if err != nil {
					t.Fatalf("Failed to create test activity: %v", err)
				}
				return map[string]interface{}{
					"activity_id": activity.ID,
				}
			},
			body: func(data map[string]interface{}) models.StudySession {
				invalidID := uint(999)
				return models.StudySession{
					StudyActivityID: data["activity_id"].(uint),
					WordGroupID:     &invalidID, // Invalid group ID
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
			setupData: func(t *testing.T) map[string]interface{} {
				return nil
			},
		},
		{
			name:   "Get Last Study Session",
			method: "GET",
			path:   "/api/dashboard/last_study_session",
			// For the "Get Last Study Session" test case
			setupData: func(t *testing.T) map[string]interface{} {
				// Create more test data
				for i := 0; i < 3; i++ {
					group, err := createTestGroup(db, fmt.Sprintf("Test Group %d", i), nil)
					if err != nil {
						t.Fatalf("Failed to create test group: %v", err)
					}

					activity, err := createTestActivity(db, fmt.Sprintf("Test Activity %d", i))
					if err != nil {
						t.Fatalf("Failed to create test activity: %v", err)
					}

					_, err = createTestStudySession(db, group.ID, activity.ID, true)
					if err != nil {
						t.Fatalf("Failed to create test session: %v", err)
					}
				}

				return map[string]interface{}{}
			},

			expectedStatus: http.StatusOK,
			validateBody: func(t *testing.T, body []byte, testData map[string]interface{}) {
				var response map[string]interface{}
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
			setupData: func(t *testing.T) map[string]interface{} {
				// Create a word first
				word, err := createTestWord(db, "테스트")
				if err != nil {
					t.Fatalf("Failed to create test word: %v", err)
				}

				return map[string]interface{}{
					"word_id": word.ID,
				}
			},
			expectedStatus: http.StatusOK,
			validateBody: func(t *testing.T, body []byte, _ map[string]interface{}) {
				var progress map[string]interface{}
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
			setupData: func(t *testing.T) map[string]interface{} {
				return nil // No setup needed
			},
			expectedStatus: http.StatusOK,
			validateBody: func(t *testing.T, body []byte, _ map[string]interface{}) {
				var stats map[string]interface{}
				assert.NoError(t, json.Unmarshal(body, &stats))

				// Basic validation of response structure
				assert.Contains(t, stats, "total_sessions")
				assert.Contains(t, stats, "active_groups")
				assert.Contains(t, stats, "success_rate")
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Reset database before test
			if err := resetTestDB(db); err != nil {
				t.Fatalf("Failed to reset database: %v", err)
			}

			// Setup test data
			var testData map[string]interface{}
			if tt.setupData != nil {
				testData = tt.setupData(t)
			}

			// Prepare request
			var req *http.Request
			if tt.body != nil {
				var bodyBytes []byte
				var err error

				if s, ok := tt.body.(string); ok {
					bodyBytes = []byte(s)
				} else if bodyFn, ok := tt.body.(func(map[string]interface{}) models.StudySession); ok && testData != nil {
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

			// Validate response
			assert.Equal(t, tt.expectedStatus, w.Code)
			if tt.validateBody != nil && w.Code == tt.expectedStatus && w.Code < 400 {
				tt.validateBody(t, w.Body.Bytes(), testData)
			}
		})
	}
}
