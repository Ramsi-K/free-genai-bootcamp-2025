# Backend Server Technical Sepcs

## Business Goal

A language learning school wants to build a prototype of learning portal which will act as three things:

- Inventory of possible vocabulary that can be learned
- Act as a  Learning record store (LRS), providing correct and wrong score on practice vocabulary
- A unified launchpad to launch different learning apps

## Technical Requirements

- The backend will be built using Go
- The database will be SQLite3
- The API will be built using Gin
-Mage is a task runner for Go.
- The API will always return JSON
- There will no authentication or authorization
- Everything be treated as a single user

## Directory Structure

```text
backend_go/
├── cmd/
│   └── server/
├── internal/
│   ├── models/     # Data structures and database operations
│   ├── handlers/   # HTTP handlers organized by feature (dashboard, words, groups, etc.)
│   └── service/    # Business logic
├── db/
│   ├── migrations/
│   └── seeds/      # For initial data population
├── magefile.go
├── go.mod
└── words.db
```

## Database Schema

Our database will be a single sqlite database called `words.db` that will be in the root of the project folder of `backend_go`

We have the following tables:

- words - stored vocabulary words
  - id integer
  - japasese string
  - romaji string
  - english string
  - parts json
- words_groups - join table for words and groups many-to-many
  - id integer
  - word_id integer
  - group_id integer
- groups - thematic groups of words
  - id integer
  - name string
- study_sessions - records of study sessions grouping word_review_items
  - id integer
  - group_id integer
  - created_at datetime
  - study_activity_id integer
- study_activities - a specific study activity, linking a study session to group
  - id integer
  - study_session_id integer
  - group_id integer
  - created_at datetime
- word_review_items - a record of word practice, determining if the word was correct or not
  - word_id integer
  - study_session_id integer
  - correct boolean
  - created_at datetime

## API Endpoints

### GET /api/dashboard/last_study_session

Returns information about the most recent study session.

#### JSON Response

```json
{
  "id": 123,
  "group_id": 456,
  "created_at": "2025-02-08T17:20:23-05:00",
  "study_activity_id": 789,
  "group_id": 456,
  "group_name": "Basic Greetings"
}
```

### GET /api/dashboard/study_progress

Returns study progress statistics.
Please note that the frontend will determine progress bar basedon total words studied and total available words.

#### JSON Response

```json
{
  "total_words_studied": 3,
  "total_available_words": 124,
}
```

### GET /api/dashboard/quick-stats

Returns quick overview statistics.

#### JSON Response

```json
{
  "success_rate": 80.0,
  "total_study_sessions": 4,
  "total_active_groups": 3,
  "study_streak_days": 4
}
```

### GET /api/study_activities/:id

#### JSON Response

```json
{
  "id": 1,
  "name": "Vocabulary Quiz",
  "thumbnail_url": "https://example.com/thumbnail.jpg",
  "description": "Practice your vocabulary with flashcards"
}
```

### GET /api/study_activities/:id/study_sessions

- pagination with 100 items per page

```json
{
  "items": [
    {
      "id": 123,
      "activity_name": "Vocabulary Quiz",
      "group_name": "Basic Greetings",
      "start_time": "2025-02-08T17:20:23-05:00",
      "end_time": "2025-02-08T17:30:23-05:00",
      "review_items_count": 20
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_items": 100,
    "items_per_page": 20
  }
}
```

### POST /api/study_activities

#### Request Params

- group_id integer
- study_activity_id integer

#### JSON Response

{
  "id": 124,
  "group_id": 123
}

### GET /api/words

- pagination with 100 items per page

#### JSON Response

```json
{
  "items": [
    {
      "japanese": "こんにちは",
      "romaji": "konnichiwa",
      "english": "hello",
      "correct_count": 5,
      "wrong_count": 2
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_items": 500,
    "items_per_page": 100
  }
}
```

### GET /api/words/:id

#### JSON Response

```json
{
  "japanese": "こんにちは",
  "romaji": "konnichiwa",
  "english": "hello",
  "stats": {
    "correct_count": 5,
    "wrong_count": 2
  },
  "groups": [
    {
      "id": 1,
      "name": "Basic Greetings"
    }
  ]
}
```

### GET /api/groups

- pagination with 100 items per page

#### JSON Response

```json
{
  "items": [
    {
      "id": 1,
      "name": "Basic Greetings",
      "word_count": 20
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 1,
    "total_items": 10,
    "items_per_page": 100
  }
}
```

### GET /api/groups/:id

#### JSON Response

```json
{
  "id": 1,
  "name": "Basic Greetings",
  "stats": {
    "total_word_count": 20
  }
}
```

### GET /api/groups/:id/words

#### JSON Response

```json
{
  "items": [
    {
      "japanese": "こんにちは",
      "romaji": "konnichiwa",
      "english": "hello",
      "correct_count": 5,
      "wrong_count": 2
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 1,
    "total_items": 20,
    "items_per_page": 100
  }
}
```

### GET /api/groups/:id/study_sessions

#### JSON Response

```json
{
  "items": [
    {
      "id": 123,
      "activity_name": "Vocabulary Quiz",
      "group_name": "Basic Greetings",
      "start_time": "2025-02-08T17:20:23-05:00",
      "end_time": "2025-02-08T17:30:23-05:00",
      "review_items_count": 20
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 1,
    "total_items": 5,
    "items_per_page": 100
  }
}
```

### GET /api/study_sessions

- pagination with 100 items per page

#### JSON Response

```json
{
  "items": [
    {
      "id": 123,
      "activity_name": "Vocabulary Quiz",
      "group_name": "Basic Greetings",
      "start_time": "2025-02-08T17:20:23-05:00",
      "end_time": "2025-02-08T17:30:23-05:00",
      "review_items_count": 20
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_items": 100,
    "items_per_page": 100
  }
}
```

### GET /api/study_sessions/:id

#### JSON Response

```json
{
  "id": 123,
  "activity_name": "Vocabulary Quiz",
  "group_name": "Basic Greetings",
  "start_time": "2025-02-08T17:20:23-05:00",
  "end_time": "2025-02-08T17:30:23-05:00",
  "review_items_count": 20
}
```

### GET /api/study_sessions/:id/words

- pagination with 100 items per page

#### JSON Response

```json
{
  "items": [
    {
      "japanese": "こんにちは",
      "romaji": "konnichiwa",
      "english": "hello",
      "correct_count": 5,
      "wrong_count": 2
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 1,
    "total_items": 20,
    "items_per_page": 100
  }
}
```

### POST /api/reset_history

#### JSON Response

```json
{
  "success": true,
  "message": "Study history has been reset"
}
```

### POST /api/full_reset

#### JSON Response

```json
{
  "success": true,
  "message": "System has been fully reset"
}
```

### POST /api/study_sessions/:id/words/:word_id/review

#### Request Params

- id (study_session_id) integer
- word_id integer
- correct boolean

#### Request Payload

```json
{
  "correct": true
}
```

#### JSON Response

```json
{
  "success": true,
  "word_id": 1,
  "study_session_id": 123,
  "correct": true,
  "created_at": "2025-02-08T17:33:07-05:00"
}
```

## Task Runner Tasks

Lets list out possible tasks we need for our lang portal.

### Initialize Database

This task will initialize the sqlite database called `words.db

### Migrate Database

This task will run a series of migrations sql files on the database

Migrations live in the `migrations` folder.
The migration files will be run in order of their file name.
The file names should looks like this:

```sql
0001_init.sql
0002_create_words_table.sql
```

### Seed Data

This task will import json files and transform them into target data for our database.

All seed files live in the `seeds` folder.

In our task we should have DSL to specific each seed file and its expected group word name.

```json
[
  {
    "kanji": "払う",
    "romaji": "harau",
    "english": "to pay",
  },
  ...
]
```
