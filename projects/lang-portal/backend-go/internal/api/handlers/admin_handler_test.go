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

	// Setup
	db, err := setupTestDB()
	if err != nil {
		t.Fatalf("Failed to setup test database: %v", err)
	}

	// Setup router
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
				// Create test data
				group := models.WordGroup{
					Name:        "Test Group",
					Description: "Test Description",
					WordsCount:  1,
				}
				if err := db.Create(&group).Error; err != nil {
					t.Fatalf("Failed to create test group: %v", err)
				}

				word := models.Word{
					Hangul:       "테스트",
					Romanization: "test",
					English:      models.StringSlice{"test"},
					Type:         "noun",
					ExampleSentence: models.ExampleSentence{
						Korean:  "테스트 문장입니다.",
						English: "This is a test sentence.",
					},
					StudyStatistics: models.StudyStatistics{
						CorrectCount: 5,
						WrongCount:   2,
					},
				}
				if err := db.Create(&word).Error; err != nil {
					t.Fatalf("Failed to create test word: %v", err)
				}

				if err := db.Model(&group).Association("Words").Append(&word); err != nil {
					t.Fatalf("Failed to associate word with group: %v", err)
				}

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

				session := models.StudySession{
					GroupID:      group.ID,
					ActivityID:   activity.ID,
					CorrectCount: 5,
					WrongCount:   2,
					CompletedAt:  time.Now(),
				}
				if err := db.Create(&session).Error; err != nil {
					t.Fatalf("Failed to create test session: %v", err)
				}
			},
			expectedStatus: http.StatusOK,
			validateDB: func(t *testing.T) {
				// First verify that study sessions are gone
				var sessionCount int64
				assert.NoError(t, db.Model(&models.StudySession{}).Count(&sessionCount).Error)
				assert.Equal(t, int64(0), sessionCount, "Expected no study sessions after reset")

				// Then verify that seed data exists
				var groupCount, wordCount, activityCount int64
				assert.NoError(t, db.Model(&models.WordGroup{}).Count(&groupCount).Error)
				assert.NoError(t, db.Model(&models.Word{}).Count(&wordCount).Error)
				assert.NoError(t, db.Model(&models.StudyActivity{}).Count(&activityCount).Error)

				// We should have seed data
				assert.Greater(t, groupCount, int64(0), "Expected groups from seed data")
				assert.Greater(t, wordCount, int64(0), "Expected words from seed data")
				assert.Greater(t, activityCount, int64(0), "Expected activities from seed data")

				// Verify all word statistics are reset
				var words []models.Word
				assert.NoError(t, db.Find(&words).Error)
				for _, word := range words {
					assert.Equal(t, 0, word.StudyStatistics.CorrectCount, "Expected word statistics to be reset")
					assert.Equal(t, 0, word.StudyStatistics.WrongCount, "Expected word statistics to be reset")
				}

				// Verify word-group associations are correct
				for _, word := range words {
					var groups []models.WordGroup
					assert.NoError(t, db.Model(&word).Association("Groups").Find(&groups))
					assert.NotEmpty(t, groups, "Expected word to be associated with at least one group")
				}
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			withCleanDB(t, db, func() {
				// Setup test data
				if tt.setupData != nil {
					tt.setupData(t)
				}

				// Make request
				w := httptest.NewRecorder()
				req := httptest.NewRequest("POST", tt.path, nil)
				router.ServeHTTP(w, req)

				// Verify response status
				assert.Equal(t, tt.expectedStatus, w.Code)

				// Validate database state if needed
				if tt.validateDB != nil {
					tt.validateDB(t)
				}
			})
		})
	}
}
