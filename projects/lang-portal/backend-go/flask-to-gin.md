# Flask to Go/Gin Conversion Plan

## 1. Flask Backend Breakdown

### 1.1 Current Architecture

- **Application Factory Pattern** (app.py)
  - Blueprint registration
  - Database initialization
  - Error handling
  - Configuration management

- **SQLAlchemy Models** (models.py)

  ```python
  class Word(db.Model):
      id = db.Column(db.Integer, primary_key=True)
      hangul = db.Column(db.String, nullable=False)
      english = db.Column(JSON, nullable=False)  # Stores multiple meanings
      type = db.Column(db.String, nullable=False)
  ```

- **Route Organization** (routes/*.py)
  - Blueprint-based routing
  - Pagination support
  - JSON response formatting

- **Database Operations** (lib/db.py)
  - SQLAlchemy ORM
  - Seed data loading
  - Transaction management

### 1.2 Key Dependencies

- Flask-SQLAlchemy for ORM
- SQLite for storage
- Invoke for task automation
- Blueprint for route modularization

## 2. Go/Gin Architecture

### 2.1 Project Structure

```text
lang-portal/
├── cmd/
│   └── server/
│       └── main.go       # Application entry point
├── internal/
│   ├── api/
│   │   ├── handlers/     # Request handlers (replaces routes/)
│   │   ├── middleware/   # Custom middleware
│   │   └── router/      # Gin router setup
│   ├── models/          # Domain models
│   ├── repository/      # Database operations
│   └── service/         # Business logic
├── pkg/
│   ├── config/          # Configuration
│   └── database/        # Database connection
└── scripts/             # Migration and seed scripts
```

### 2.2 Technology Choices

#### Database Layer

- **GORM** over raw SQL because:
  - Provides similar functionality to SQLAlchemy
  - Maintains good performance with proper configuration
  - Supports migrations and relationships
  - Better type safety than raw SQL

#### API Framework

- **Gin** because:
  - High performance
  - Built-in middleware support
  - Good request validation
  - Excellent error handling

#### Data Storage

- Keep **SQLite** for development
- Design for easy migration to PostgreSQL

## 3. Key Differences & Justifications

### 3.1 Models & Database

```go
// internal/models/word.go
type Word struct {
    ID              uint      `gorm:"primaryKey"`
    Hangul          string    `gorm:"not null"`
    Romanization    string    `gorm:"not null"`
    English         []string  `gorm:"type:json;not null"` // Store as JSON
    Type            string    `gorm:"not null"`
    WordGroups      []string  `gorm:"type:json"`
    ExampleSentence struct {
        Korean  string `json:"korean"`
        English string `json:"english"`
    } `gorm:"type:json"`
    StudyStatistics struct {
        CorrectCount int `json:"correct_count"`
        WrongCount   int `json:"wrong_count"`
    } `gorm:"type:json"`
    CreatedAt       time.Time
    UpdatedAt       time.Time
}

// internal/models/word_group.go
type WordGroup struct {
    ID          uint      `gorm:"primaryKey"`
    Name        string    `gorm:"not null"`
    Description string    `gorm:"not null"`
    Words       []Word    `gorm:"many2many:group_words"`
    CreatedAt   time.Time
    UpdatedAt   time.Time
}

// internal/models/study_session.go
type StudySession struct {
    ID              uint      `gorm:"primaryKey"`
    GroupID         uint      `gorm:"index"`
    ActivityID      uint      `gorm:"index"`
    CorrectCount    int
    WrongCount      int
    CompletedAt     time.Time
    CreatedAt       time.Time
    UpdatedAt       time.Time
}

// internal/models/study_activity.go
type StudyActivity struct {
    ID          uint      `gorm:"primaryKey"`
    Name        string    `gorm:"not null"`
    Description string
    Thumbnail   string
    LaunchURL   string    `gorm:"not null"`
    CreatedAt   time.Time
    UpdatedAt   time.Time
}
```

**Justification:**

- Added all fields from frontend spec and JSON data
- Proper GORM tags for validation and DB mapping
- JSON storage for arrays and nested structures
- Added timestamp fields for tracking
- Added study statistics tracking
- Added proper relationships between models

### 3.2 API Endpoints

```go
// internal/api/router/router.go
func SetupRouter(h *handlers.Handler) *gin.Engine {
    r := gin.Default()
    
    // Words endpoints
    r.GET("/api/words", h.ListWords)
    r.GET("/api/words/:id", h.GetWord)
    
    // Groups endpoints
    r.GET("/api/groups", h.ListGroups)
    r.GET("/api/groups/:id", h.GetGroup)
    r.GET("/api/groups/:id/words", h.GetGroupWords)
    r.GET("/api/groups/:id/study_sessions", h.GetGroupStudySessions)
    
    // Dashboard endpoints
    r.GET("/api/dashboard/last_study_session", h.GetLastStudySession)
    r.GET("/api/dashboard/study_progress", h.GetStudyProgress)
    r.GET("/api/dashboard/quick_stats", h.GetQuickStats)
    
    // Study activities endpoints
    r.GET("/api/study_activities", h.ListStudyActivities)
    r.GET("/api/study_activities/:id", h.GetStudyActivity)
    r.GET("/api/study_activities/:id/study_sessions", h.GetActivityStudySessions)
    r.POST("/api/study_activities", h.CreateStudySession)
    
    // Sentence practice endpoints
    r.GET("/api/sentence_practice", h.GetPracticeSentence)
    r.POST("/api/sentence_practice/attempt", h.SubmitSentenceAttempt)
    r.GET("/api/sentence_practice/examples", h.GetSentenceExamples)
    r.GET("/api/sentence_practice/statistics", h.GetSentenceStatistics)
    
    // Settings endpoints
    r.POST("/api/reset_history", h.ResetHistory)
    r.POST("/api/full_reset", h.FullReset)
    
    return r
}
```

**Justification:**

- Complete API coverage matching frontend requirements
- RESTful endpoint design
- Proper route grouping
- Consistent naming convention

## 4. Performance Optimizations

### 4.1 Database

- Connection pooling
- Prepared statements
- Proper indexing on frequently queried fields
- Eager loading for relationships

### 4.2 Request Handling

- Middleware for common operations
- Response caching where appropriate
- Goroutines for concurrent operations
- Connection pooling

### 4.3 Memory Management

- Proper use of pointers vs values
- Buffer pooling for large operations
- Efficient JSON handling

## 5. Final Implementation Plan

### 5.1 Phase 1: Core Structure

1. Set up project structure
2. Implement database models
3. Create basic CRUD operations

### 5.2 Phase 2: API Routes

1. Implement handlers
2. Set up middleware
3. Add request validation

### 5.3 Phase 3: Data Migration

1. Create migration scripts
2. Implement seed data loading
3. Add data verification tools

### 5.4 Phase 4: Testing & Optimization

1. Unit tests
2. Integration tests
3. Performance benchmarking
4. Load testing

## 6. Migration Considerations

### 6.1 Data Migration

- Create SQLite to PostgreSQL migration tools
- Verify data integrity during migration
- Handle JSON field conversion

### 6.2 API Compatibility

- Maintain existing API contract
- Ensure response formats match
- Add version headers

## 7. Testing Strategy

### 7.1 Unit Tests

```go
func TestWordRepository_Find(t *testing.T) {
    // Test cases
}
```

### 7.2 Integration Tests

```go
func TestWordAPI_List(t *testing.T) {
    // API test cases
}
```

## 8. Documentation

### 8.1 API Documentation

- OpenAPI/Swagger specs
- Handler documentation
- Example requests/responses

### 8.2 Development Documentation

- Setup instructions
- Configuration guide
- Deployment process
