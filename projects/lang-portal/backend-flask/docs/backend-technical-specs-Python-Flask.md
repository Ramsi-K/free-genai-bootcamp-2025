# Backend Server Technical Specs: Python + Flask (Korean)

This document outlines the technical specifications for converting the existing Go + Gin (Japanese) API into a Python + Flask (Korean) API. The goal is to create a learning portal backend that manages Korean vocabulary, study sessions, and user progress.

## Business Goal

A language learning school wants to build a prototype of a learning portal which will act as three things:

* **Inventory of possible vocabulary** that can be learned.
* Act as a **Learning Record Store (LRS)**, providing correct and wrong score on practice vocabulary.
* A **unified launchpad** to launch different learning apps.

## Technical Requirements

* The backend will be built using **Python**.
* The database will be **SQLite3**.
* The API will be built using **Flask and Flask Blueprints**.
* **SQLAlchemy ORM** will be used for database models.
* The API will always return **JSON**.
* There will be **no authentication or authorization**.
* Everything will be treated as a **single user**.

## Directory Structure

The file structure will follow Flask conventions:

* `app.py`: Main application file.
* `routes/`: Contains Flask Blueprints for different API endpoints.
* `models.py`: Defines SQLAlchemy database models.
* `db.py`: Manages the database connection and initialization.
* `migrations/`: Alembic migrations for database schema changes.
* `instance/`: Contains the SQLite database file (`words.db`).

## Database Schema

The database will be a single SQLite database called `words.db`. The schema reflects Korean vocabulary:

* * **words** - Stored vocabulary words.
  * `id` (integer, primary key)
  * `hangul` (string): Korean Hangul representation.
  * `romanization` (string): Romanized version of the word.
  * `english` (string): English translation.
  * `type` (string): Part of speech (noun, verb, etc.).  
  * `example_korean` (string): Example sentence in Korean.  
  * `example_english` (string): Example sentence in English.  

* **words\_groups** - Join table for words and groups (many-to-many).
  * `id` (integer, primary key)
  * `word_id` (integer, foreign key referencing words.id).
  * `group_id` (integer, foreign key referencing groups.id).
* **groups** - Thematic groups of words.
  * `id` (integer, primary key)
  * `name` (string).
  * `words_count` (integer, default: 0): Counter for words in the group.
* **study\_sessions** - Records of study sessions grouping word\_review\_items.
  * `id` (integer, primary key)
  * `group_id` (integer, foreign key referencing groups.id).
  * `created_at` (datetime, default: current time).
  * `study_activity_id` (integer, foreign key referencing study\_activities.id).
* **study\_activities** - A specific study activity, linking a study session to a group.
  * `id` (integer, primary key)
  * `study_session_id` (integer).
  * `group_id` (integer).
  * `created_at` (datetime).
  * `name` (string).
  * `url` (string).
  * `thumbnail_url` (string): URL for a thumbnail image representing the activity.
* **word\_review\_items** - A record of word practice, determining if the word was correct or not.
  * `id` (integer, primary key).
  * `word_id` (integer, foreign key referencing words.id).
  * `study_session_id` (integer, foreign key referencing study\_sessions.id).
  * `correct` (boolean).
  * `created_at` (datetime, default: current time).

## API Endpoints

The API endpoints remain the same but are implemented as Flask route definitions using Flask Blueprints.

* `GET /api/dashboard/last_study_session`: Returns information about the most recent study session.
* `GET /api/dashboard/study_progress`: Returns study progress statistics.
* `GET /api/dashboard/quick-stats`: Returns quick overview statistics.
* `GET /api/study_activities/:id`
  * **Response Format:**

        ```json
        {
            "id": 1,
            "name": "Flashcards",
            "url": "/flashcards",
            "thumbnail_url": "/images/flashcard_thumb.png",
            "study_session_id": 123,
            "group_id": 456,
            "created_at": "2024-01-01T12:00:00"
        }
        ```

* `GET /api/study_activities/:id/study_sessions`: Pagination with 100 items per page.
* `POST /api/study_activities`: Requires `group_id` and `study_activity_id` as request parameters.
* `GET /api/words`: Pagination with 100 items per page.
  * **JSON Response Example:**

        ```json
          [
            {
                "id": 1,
                "hangul": "학교",
                "romanization": "hakgyo",
                "english": "school",
                "type": "noun",
                "example": {
                    "korean": "나는 학교에 갑니다.",
                    "english": "I go to school."
                }
            },
            {
                "id": 2,
                "hangul": "선생님",
                "romanization": "seonsaengnim",
                "english": "teacher",
                "type": "noun",
                "example": {
                    "korean": "우리 선생님은 친절하십니다.",
                    "english": "Our teacher is kind."
                }
            }
        ]
        ```

* `GET /api/words/:id`.
  * **JSON Response Example:**

        ```json
        {
                "id": 1,
                "hangul": "학교",
                "romanization": "hakgyo",
                "english": "school",
                "type": "noun",
                "example": {
                    "korean": "나는 학교에 갑니다.",
                    "english": "I go to school."
                }
        }
        ```

* `GET /api/groups`: Pagination with 100 items per page.
  * **JSON Response Example:**

        ```json
        [
            {
                "id": 1,
                "name": "Basic Korean",
                "words_count": 20
            },
            {
                "id": 2,
                "name": "Travel Phrases",
                "words_count": 15
            }
        ]
        ```

* `GET /api/groups/:id`.
  * **JSON Response Example:**

        ```json
        {
            "id": 1,
            "name": "Basic Korean",
            "words_count": 20
        }
        ```

* `GET /api/groups/:id/words`.
  * **JSON Response Example:**

        ```json
        [
            {
                "id": 1,
                "hangul": "학교",
                "romanization": "hakgyo",
                "english": "school",
                "type": "noun",
                "example": {
                    "korean": "나는 학교에 갑니다.",
                    "english": "I go to school."
                }
            },
            {
                "id": 2,
                "hangul": "선생님",
                "romanization": "seonsaengnim",
                "english": "teacher",
                "type": "noun",
                "example": {
                    "korean": "우리 선생님은 친절하십니다.",
                    "english": "Our teacher is kind."
                }
            }
        ]
        ```

* `GET /api/groups/:id/study_sessions`.
  * **JSON Response Example:**

        ```json
        [
            {
                "id": 1,
                "group_id": 1,
                "created_at": "2024-01-05T10:00:00",
                "study_activity_id": 1
            },
            {
                "id": 2,
                "group_id": 1,
                "created_at": "2024-01-05T11:00:00",
                "study_activity_id": 2
            }
        ]
        ```

* `GET /api/study_sessions`: Pagination with 100 items per page.
  * **JSON Response Example:**

        ```json
        [
            {
                "id": 1,
                "group_id": 1,
                "created_at": "2024-01-05T10:00:00",
                "study_activity_id": 1
            },
            {
                "id": 2,
                "group_id": 1,
                "created_at": "2024-01-05T11:00:00",
                "study_activity_id": 2
            }
        ]
        ```

* `GET /api/study_sessions/:id`.
  * **JSON Response Example:**

        ```json
        {
            "id": 1,
            "group_id": 1,
            "created_at": "2024-01-05T10:00:00",
            "study_activity_id": 1
        }
        ```

* `GET /api/study_sessions/:id/words`: Pagination with 100 items per page.
  * **JSON Response Example:**

        ```json
        [
            {
                "id": 1,
                "hangul": "학교",
                "romanization": "hakgyo",
                "english": "school",
                "type": "noun",
                "example": {
                    "korean": "나는 학교에 갑니다.",
                    "english": "I go to school."
                }
            },
            {
                "id": 2,
                "hangul": "선생님",
                "romanization": "seonsaengnim",
                "english": "teacher",
                "type": "noun",
                "example": {
                    "korean": "우리 선생님은 친절하십니다.",
                    "english": "Our teacher is kind."
                }
            }
        ]
        ```

* `POST /api/reset_history`.
  * **JSON Response Example:**

        ```json
        { "status": "success", "message": "Study history reset." }
        ```

* `POST /api/full_reset`.
  * **JSON Response Example:**

        ```json
        { "status": "success", "message": "Database fully reset." }
        ```

* `POST /api/study_sessions/:id/words/:word_id/review`: Requires `id` (study\_session\_id), `word_id`, and `correct` as request parameters.
  * **JSON Response Example:**

        ```json
        { "status": "success", "message": "Review recorded." }
        ```

* `POST /api/study_sessions`: Creates a **new study session** for a group.
  * **JSON Response Example:**

        ```json
        { "id": 124, "group_id": 123 }
        ```

* `POST /api/study_sessions/:id/review`: Logs a **review attempt** for a word during a study session.

## Query Parameters

All query parameters (`page`, `sort_by`, `order`) and pagination work the same way in Flask as described in the original specification.

* **For `/words` endpoint:**
  * `page`: Page number (default: 1).
  * `sort_by`: Sort field (`hangul`, `romanization`, `english`, `type`,`correct_count`, `wrong_count`) (default: `hangul`).
  * `order`: Sort order (`asc`, `desc`) (default: `asc`).
* **For `/groups` endpoint:**
  * `page`: Page number (default: 1).
  * `sort_by`: Sort field (`name`, `words_count`) (default: `name`).
  * `order`: Sort order (`asc`, `desc`) (default: `asc`).

## Error Handling

* **404 Errors:**
  * Return a JSON response with a `404 Not Found` status code.
  * Include an error message indicating the resource was not found.

        ```json
        { "error": "Resource not found" }
        ```

* **Validation Errors:**
  * Return a JSON response with a `400 Bad Request` status code.
  * Include a detailed error message describing the validation failure.

        ```json
        { "error": "Invalid input", "message": "group_id is required" }
        ```

## Task Runner Tasks

* **Initialize Database:** Creates the SQLite database called `words.db`.
* **Migrate Database:** Runs a series of migration SQL files on the database using Alembic.

  * **Alembic Migration File Structure:**
    * Alembic uses a `versions/` directory to store migration scripts.
    * Each migration file has a unique autogenerated name, typically including a timestamp. Example: `versions/1234abcd5678_add_thumbnail_url_to_study_activities.py`
    * Each file contains `upgrade()` and `downgrade()` functions to apply and revert the changes.
* **Seed Data:** Imports JSON files and transforms them into target data for our database. Seed files live in the `seeds` folder.
I
