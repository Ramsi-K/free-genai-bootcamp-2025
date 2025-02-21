package handlers

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/models"
	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/repository"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"gorm.io/gorm"
)

// MockGroupRepository is a mock implementation of the repository.GroupRepository interface
type MockGroupRepository struct {
	mock.Mock
}

func (m *MockGroupRepository) ListGroups() ([]models.WordGroup, error) {
	args := m.Called()
	return args.Get(0).([]models.WordGroup), args.Error(1)
}

func (m *MockGroupRepository) GetGroup(id uint) (*models.WordGroup, error) {
	args := m.Called(id)
	if args.Get(0) == nil {
		return nil, gorm.ErrRecordNotFound
	}
	return args.Get(0).(*models.WordGroup), args.Error(1)
}

func (m *MockGroupRepository) GetGroupWithWords(id uint) (*models.WordGroup, error) {
	args := m.Called(id)
	if args.Get(0) == nil {
		return nil, gorm.ErrRecordNotFound
	}
	return args.Get(0).(*models.WordGroup), args.Error(1)
}

func (m *MockGroupRepository) GetGroupStudySessions(groupID uint) ([]models.StudySession, error) {
	args := m.Called(groupID)
	return args.Get(0).([]models.StudySession), args.Error(1)
}

func (m *MockGroupRepository) Create(group *models.WordGroup) error {
	args := m.Called(group)
	return args.Error(0)
}

func (m *MockGroupRepository) Update(group *models.WordGroup) error {
	args := m.Called(group)
	return args.Error(0)
}

func (m *MockGroupRepository) Delete(id uint) error {
	args := m.Called(id)
	return args.Error(0)
}

// Unit Tests
func TestListGroups(t *testing.T) {
	// Setup
	gin.SetMode(gin.TestMode)
	mockRepo := new(MockGroupRepository)
	handler := NewGroupHandler(mockRepo)

	testCases := []struct {
		name           string
		setupMock      func()
		expectedStatus int
		expectedLen    int
	}{
		{
			name: "Success - Empty List",
			setupMock: func() {
				mockRepo.On("ListGroups").Return([]models.WordGroup{}, nil).Once()
			},
			expectedStatus: http.StatusOK,
			expectedLen:    0,
		},
		{
			name: "Success - Multiple Groups",
			setupMock: func() {
				mockRepo.On("ListGroups").Return([]models.WordGroup{
					{
						Name:        "Group 1",
						Description: "Description 1",
						WordsCount:  2,
					},
					{
						Name:        "Group 2",
						Description: "Description 2",
						WordsCount:  3,
					},
				}, nil).Once()
			},
			expectedStatus: http.StatusOK,
			expectedLen:    2,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			// Setup mock
			tc.setupMock()

			// Setup router and recorder
			w := httptest.NewRecorder()
			c, _ := gin.CreateTestContext(w)

			// Call handler
			handler.ListGroups(c)

			// Assert response
			assert.Equal(t, tc.expectedStatus, w.Code)

			if w.Code == http.StatusOK {
				var response struct {
					Data []models.WordGroup `json:"data"`
				}
				err := json.Unmarshal(w.Body.Bytes(), &response)
				assert.NoError(t, err)
				assert.Len(t, response.Data, tc.expectedLen)
			}

			mockRepo.AssertExpectations(t)
		})
	}
}

func TestGetGroup(t *testing.T) {
	gin.SetMode(gin.TestMode)
	mockRepo := new(MockGroupRepository)
	handler := NewGroupHandler(mockRepo)

	testCases := []struct {
		name           string
		groupID        string
		setupMock      func()
		expectedStatus int
	}{
		{
			name:    "Success",
			groupID: "1",
			setupMock: func() {
				mockRepo.On("GetGroup", uint(1)).Return(&models.WordGroup{
					Model: gorm.Model{ID: 1},
					Name:  "Test Group",
				}, nil)
			},
			expectedStatus: http.StatusOK,
		},
		{
			name:           "Invalid ID",
			groupID:        "invalid",
			setupMock:      func() {},
			expectedStatus: http.StatusBadRequest,
		},
		{
			name:    "Group Not Found",
			groupID: "999",
			setupMock: func() {
				mockRepo.On("GetGroup", uint(999)).Return(nil, gorm.ErrRecordNotFound)
			},
			expectedStatus: http.StatusNotFound,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			// Setup mock
			tc.setupMock()

			// Setup router and recorder
			w := httptest.NewRecorder()
			c, _ := gin.CreateTestContext(w)
			c.Params = gin.Params{{Key: "id", Value: tc.groupID}}

			// Call handler
			handler.GetGroup(c)

			// Assert response
			assert.Equal(t, tc.expectedStatus, w.Code)

			if w.Code == http.StatusOK {
				var group models.WordGroup
				err := json.Unmarshal(w.Body.Bytes(), &group)
				assert.NoError(t, err)
				assert.NotEmpty(t, group.Name)
			}

			mockRepo.AssertExpectations(t)
		})
	}
}

// Integration Tests
func TestGroupHandler_Integration(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test")
	}

	// Setup
	db, err := setupTestDB() // Using clean DB without seed data
	if err != nil {
		t.Fatalf("Failed to setup test database: %v", err)
	}
	defer cleanupTestDB(db)

	// Create test data
	word1, err := createTestWord(db, "테스트1")
	if err != nil {
		t.Fatalf("Failed to create test word: %v", err)
	}

	word2, err := createTestWord(db, "테스트2")
	if err != nil {
		t.Fatalf("Failed to create test word: %v", err)
	}

	group, err := createTestGroup(db, "Test Group", []models.Word{*word1, *word2})
	if err != nil {
		t.Fatalf("Failed to create test group: %v", err)
	}

	activity, err := createTestActivity(db, "Test Activity")
	if err != nil {
		t.Fatalf("Failed to create test activity: %v", err)
	}

	session, err := createTestStudySession(db, group.ID, activity.ID, true)
	if err != nil {
		t.Fatalf("Failed to create test session: %v", err)
	}

	// Setup router
	gin.SetMode(gin.TestMode)
	router := gin.New()
	repo := repository.NewGroupRepository(repository.NewBaseRepository(db))
	handler := NewGroupHandler(repo)

	router.GET("/api/groups", handler.ListGroups)
	router.GET("/api/groups/:id", handler.GetGroup)
	router.GET("/api/groups/:id/words", handler.GetGroupWords)
	router.GET("/api/groups/:id/study_sessions", handler.GetGroupStudySessions)

	// Test cases
	tests := []struct {
		name           string
		path           string
		expectedStatus int
		validateBody   func(t *testing.T, body []byte)
	}{
		{
			name:           "List Groups",
			path:           "/api/groups",
			expectedStatus: http.StatusOK,
			validateBody: func(t *testing.T, body []byte) {
				var response struct {
					Data []models.WordGroup `json:"data"`
				}
				assert.NoError(t, json.Unmarshal(body, &response))
				assert.Len(t, response.Data, 1)
				group := response.Data[0]
				assert.Equal(t, "Test Group", group.Name)
				assert.Equal(t, "Test Description", group.Description)
				assert.Equal(t, 2, group.WordsCount)
				assert.NotZero(t, group.CreatedAt)
				assert.NotZero(t, group.UpdatedAt)
			},
		},
		{
			name:           "Get Group",
			path:           "/api/groups/1",
			expectedStatus: http.StatusOK,
			validateBody: func(t *testing.T, body []byte) {
				var group models.WordGroup
				assert.NoError(t, json.Unmarshal(body, &group))
				assert.Equal(t, uint(1), group.ID)
				assert.Equal(t, "Test Group", group.Name)
				assert.Equal(t, "Test Description", group.Description)
				assert.Equal(t, 2, group.WordsCount)
				assert.NotZero(t, group.CreatedAt)
				assert.NotZero(t, group.UpdatedAt)
			},
		},
		{
			name:           "Get Group Words",
			path:           "/api/groups/1/words",
			expectedStatus: http.StatusOK,
			validateBody: func(t *testing.T, body []byte) {
				var response struct {
					Data []models.Word `json:"data"`
				}
				assert.NoError(t, json.Unmarshal(body, &response))
				assert.Len(t, response.Data, 2)
				for _, word := range response.Data {
					assert.NotEmpty(t, word.ID)
					assert.NotEmpty(t, word.Hangul)
					assert.NotEmpty(t, word.Romanization)
					assert.NotEmpty(t, word.Type)
					assert.NotEmpty(t, word.EnglishTranslations)
					assert.NotEmpty(t, word.Sentences[0].Korean)
					assert.NotEmpty(t, word.Sentences[0].English)
					assert.NotZero(t, word.CreatedAt)
					assert.NotZero(t, word.UpdatedAt)
				}
			},
		},
		{
			name:           "Get Group Study Sessions",
			path:           "/api/groups/1/study_sessions",
			expectedStatus: http.StatusOK,
			validateBody: func(t *testing.T, body []byte) {
				var response struct {
					Data []models.StudySession `json:"data"`
				}
				assert.NoError(t, json.Unmarshal(body, &response))
				assert.Len(t, response.Data, 1)
				studySession := response.Data[0]
				assert.Equal(t, session.ID, studySession.ID)
				assert.Equal(t, session.WordGroupID, studySession.WordGroupID)
				assert.Equal(t, session.StudyActivityID, studySession.StudyActivityID)
				assert.Equal(t, session.CorrectCount, studySession.CorrectCount)
				assert.Equal(t, session.WrongCount, studySession.WrongCount)
			},
		},
		{
			name:           "Get Non-existent Group",
			path:           "/api/groups/999",
			expectedStatus: http.StatusNotFound,
		},
		{
			name:           "Get Group with Invalid ID",
			path:           "/api/groups/invalid",
			expectedStatus: http.StatusBadRequest,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Reset database before each test
			if err := resetTestDB(db); err != nil {
				t.Fatalf("Failed to reset test database: %v", err)
			}

			// Create test data again after reset
			word1, err = createTestWord(db, "테스트1")
			if err != nil {
				t.Fatalf("Failed to create test word: %v", err)
			}

			word2, err = createTestWord(db, "테스트2")
			if err != nil {
				t.Fatalf("Failed to create test word: %v", err)
			}

			group, err = createTestGroup(db, "Test Group", []models.Word{*word1, *word2})
			if err != nil {
				t.Fatalf("Failed to create test group: %v", err)
			}

			activity, err = createTestActivity(db, "Test Activity")
			if err != nil {
				t.Fatalf("Failed to create test activity: %v", err)
			}

			session, err = createTestStudySession(db, group.ID, activity.ID, true)
			if err != nil {
				t.Fatalf("Failed to create test session: %v", err)
			}

			w := httptest.NewRecorder()
			req := httptest.NewRequest("GET", tt.path, nil)
			router.ServeHTTP(w, req)

			assert.Equal(t, tt.expectedStatus, w.Code)
			if tt.validateBody != nil && w.Code == http.StatusOK {
				tt.validateBody(t, w.Body.Bytes())
			}
		})
	}
}
