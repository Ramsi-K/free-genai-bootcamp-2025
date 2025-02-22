package handlers

import (
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/models"
	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
)

func TestAdminHandler_Integration(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test")
	}

	// Setup test database
	db, err := setupTestDB()
	if err != nil {
		t.Fatalf("Failed to setup test database: %v", err)
	}

	// Setup router and admin handler
	gin.SetMode(gin.TestMode)
	router := gin.New()
	handler := NewAdminHandler(db)

	router.POST("/api/admin/reset/history", handler.ResetHistory)
	router.POST("/api/admin/reset/full", handler.FullReset)

	// Test cases
	tests := []struct {
		name           string
		path           string
		setupData      func(t *testing.T)
		expectedStatus int
		validateDB     func(t *testing.T)
	}{
		{
			name: "Full Reset",
			path: "/api/admin/reset/full",
			setupData: func(t *testing.T) {
				// Create a test word group
				group := models.WordGroup{
					Name:        "Test Group",
					Description: "Test Description",
					WordsCount:  1,
				}
				if err := db.Create(&group).Error; err != nil {
					t.Fatalf("Failed to create test group: %v", err)
				}

				// Create a GROUP_Word record (using the new model) directly
				groupWord := models.GROUP_Word{
					WordGroupID:  group.ID,
					Hangul:       "테스트",
					Romanization: "test",
				}
				if err := db.Create(&groupWord).Error; err != nil {
					t.Fatalf("Failed to create group word: %v", err)
				}

				// Create a test study activity
				activity := models.StudyActivity{
					Name:        "Test Activity",
					Description: "Test Description",
					Type:        "test",
					Thumbnail:   "/test.png",
					LaunchURL:   "/test",
				}
				if err := db.Create(&activity).Error; err != nil {
					t.Fatalf("Failed to create test activity: %v", err)
				}

				// Create a test study session linked to the group
				session := models.StudySession{
					WordGroupID:     &group.ID,
					StudyActivityID: activity.ID,
					CorrectCount:    5,
					WrongCount:      2,
					CompletedAt:     time.Now(),
				}
				if err := db.Create(&session).Error; err != nil {
					t.Fatalf("Failed to create test session: %v", err)
				}
			},
			expectedStatus: http.StatusOK,
			validateDB: func(t *testing.T) {
				// Verify that study sessions have been reset (after full reset, expect none)
				var sessionCount int64
				assert.NoError(t, db.Model(&models.StudySession{}).Count(&sessionCount).Error)
				assert.Equal(t, int64(0), sessionCount, "Expected no study sessions after reset")

				// Verify that seed data exists for word groups, group words, and study activities.
				var groupCount, groupWordCount, activityCount int64
				assert.NoError(t, db.Model(&models.WordGroup{}).Count(&groupCount).Error)
				assert.NoError(t, db.Model(&models.GROUP_Word{}).Count(&groupWordCount).Error)
				assert.NoError(t, db.Model(&models.StudyActivity{}).Count(&activityCount).Error)
				assert.Greater(t, groupCount, int64(0), "Expected groups from seed data")
				assert.Greater(t, groupWordCount, int64(0), "Expected group words from seed data")
				assert.Greater(t, activityCount, int64(0), "Expected activities from seed data")
			},
		},
	}

	// Run test cases
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			withCleanDB(t, db, func() {
				if tt.setupData != nil {
					tt.setupData(t)
				}

				// Make the HTTP request
				w := httptest.NewRecorder()
				req := httptest.NewRequest("POST", tt.path, nil)
				router.ServeHTTP(w, req)

				// Verify response status
				assert.Equal(t, tt.expectedStatus, w.Code)

				if tt.validateDB != nil {
					tt.validateDB(t)
				}
			})
		})
	}
}
