package handlers

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strconv"
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

	// Setup test DB
	db, err := setupTestDB()
	if err != nil {
		t.Fatalf("Failed to setup test database: %v", err)
	}
	defer cleanupTestDB(db)

	// Setup router, repository, and handler
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
				activity, err := createTestActivity(db, "Test Activity")
				if err != nil {
					t.Fatalf("Failed to create test activity: %v", err)
				}
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
				assert.Len(t, response.Data, 1)
				assert.Equal(t, "Test Activity", response.Data[0].Name)
			},
		},
		{
			name:   "Get Activity",
			method: "GET",
			// Initially leave path empty; it will be updated below based on setupData.
			path: "",
			setupData: func(t *testing.T) map[string]any {
				activity, err := createTestActivity(db, "Test Activity")
				if err != nil {
					t.Fatalf("Failed to create test activity: %v", err)
				}
				return map[string]any{
					"activity_id": activity.ID,
				}
			},
			expectedStatus: http.StatusOK,
			validateBody: func(t *testing.T, body []byte, data map[string]any) {
				var activity models.StudyActivity
				assert.NoError(t, json.Unmarshal(body, &activity))
				assert.Equal(t, "Test Activity", activity.Name)
			},
		},
		{
			name:   "Create Study Session - Valid Data",
			method: "POST",
			path:   "/api/study_activities",
			setupData: func(t *testing.T) map[string]any {
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
			setupData: func(t *testing.T) map[string]any {
				group, err := createTestGroup(db, "Test Group", nil)
				if err != nil {
					t.Fatalf("Failed to create test group: %v", err)
				}
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
				activity, err := createTestActivity(db, "Test Activity")
				if err != nil {
					t.Fatalf("Failed to create test activity: %v", err)
				}
				return map[string]any{
					"activity_id": activity.ID,
				}
			},
			body: func(data map[string]any) models.StudySession {
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
			setupData: func(t *testing.T) map[string]any {
				return nil
			},
		},
		{
			name:   "Get Last Study Session",
			method: "GET",
			path:   "/api/dashboard/last_study_session",
			setupData: func(t *testing.T) map[string]any {
				// Create additional test data
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
				// Create a test word
				word, err := createTestWord(db, "테스트")
				if err != nil {
					t.Fatalf("Failed to create test word: %v", err)
				}
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

			// Setup test data (if any)
			var testData map[string]any
			if tt.setupData != nil {
				testData = tt.setupData(t)
			}

			// For "Get Activity" test case, update the path using the created activity_id
			if tt.name == "Get Activity" {
				if id, ok := testData["activity_id"].(uint); ok {
					tt.path = "/api/study_activities/" + strconv.Itoa(int(id))
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
