<!-- markdownlint-disable MD024 -->

# Frontend Technical Spec (English - Korean JSON Format)

## **📌 JSON Data Structures**

## Word Data Structure

```json
{
  "id": 1,
  "hangul": "학교",
  "romanization": "hakgyo",
  "type": "noun",
  "english": ["school"],
  "example_sentence": {
    "korean": "그는 학교에서 저보다 한 학년 위였어요.",
    "english": "He was a year ahead of me in school."
  },
  "study_statistics": {
    "correct_count": 10,
    "wrong_count": 2
  },
  "created_at": "2024-03-15T10:00:00Z",
  "updated_at": "2024-03-15T10:00:00Z"
}
```

## Word Group Data Structure

```json
{
  "id": 1,
  "name": "School-related Words",
  "description": "Words related to education and school life",
  "words": [
    {
      "hangul": "학교",
      "romanization": "hakgyo",
      "english": ["school"]
    }
  ],
  "created_at": "2024-03-15T10:00:00Z",
  "updated_at": "2024-03-15T10:00:00Z"
}
```

## Study Session Data Structure

```json
{
  "id": 1,
  "group_id": 1,
  "activity_id": 1,
  "correct_count": 8,
  "wrong_count": 2,
  "completed_at": "2024-03-15T10:30:00Z",
  "created_at": "2024-03-15T10:00:00Z",
  "updated_at": "2024-03-15T10:30:00Z"
}
```

## Study Activity Data Structure

```json
{
  "id": 1,
  "name": "Typing Practice",
  "description": "Practice typing Korean words",
  "thumbnail": "typing_practice.png",
  "launch_url": "/activities/typing",
  "created_at": "2024-03-15T10:00:00Z",
  "updated_at": "2024-03-15T10:00:00Z"
}
```

# **📌 JSON Data Sources for API Endpoints**

| **API Endpoint**                            | **JSON/Data Source**          | **What It Retrieves**                                  | **Notes** |
|---------------------------------------------|------------------------------|------------------------------------------------------|----------|
| `GET /api/words`                            | `data_korean.json`           | Retrieves paginated word list                        | Used for general word browsing |
| `GET /api/words/:id`                        | `data_korean.json`           | Fetches detailed word info + example sentences      | Includes `groups` field for thematic categorization |
| `GET /api/groups`                           | `word_groups.json`           | Retrieves list of thematic word groups              | Groups like "Food," "School," "Shopping" |
| `GET /api/groups/:id`                       | `word_groups.json`           | Fetches words assigned to a specific word group     | Ensures words belong to correct categories |
| `GET /api/groups/:id/words`                 | `word_groups.json`           | Retrieves words inside a thematic category          | Example: "School" group contains "학생," "책" |
| `GET /api/groups/:id/study_sessions`        | Database (Tracked Data)      | Fetches study session history for a word group      | Requires database storage |
| `GET /api/dashboard/last_study_session`     | Database (Tracked Data)      | Fetches last study session details                  | Requires user tracking |
| `GET /api/dashboard/study_progress`         | Database (Tracked Data)      | Retrieves overall study progress                    | Shows percentage of words mastered |
| `GET /api/dashboard/quick_stats`            | Database (Tracked Data)      | Returns quick stats (success rate, active groups)   | Used in the dashboard UI |
| `GET /api/sentence_practice`                | `data_korean.json`           | Fetches example sentences for practice              | Pulls from `example` field in words JSON |
| `POST /api/sentence_practice/attempt`       | Database (Tracked Data)      | Submits user-translated sentence for evaluation     | Stores user attempts and grading |
| `GET /api/sentence_practice/examples`       | `data_korean.json`           | Fetches example sentences for a specific word       | `/api/sentence_practice/examples?word=학생` |
| `GET /api/sentence_practice/statistics`     | Database (Tracked Data)      | Retrieves user progress in sentence practice        | Tracks accuracy, attempts, and improvement |
| `GET /api/study_activities`                 | `study_activities.json`      | Fetches available study activities                  | Example: "Typing Tutor" app |
| `GET /api/study_activities/:id`             | `study_activities.json`      | Retrieves details of a study activity               | Provides activity name and launch URL |
| `GET /api/study_activities/:id/study_sessions` | Database (Tracked Data)   | Retrieves past study sessions for an activity       | Tracks session attempts |
| `POST /api/study_activities`                | Database (Tracked Data)      | Creates a new study session                         | Logs study session metadata |
| `POST /api/reset_history`                   | Database (Tracked Data)      | Resets user study history                           | Deletes past sessions and progress |
| `POST /api/full_reset`                      | Database (Tracked Data)      | Drops and reseeds all data                          | Full reset of learning progress |

##

### Dashboard `/dashboard`

#### Purpose

This page provides a summary of learning progress and serves as the default page when a user visits the web app.

#### Components

- **Last Study Session**
  - Shows the last activity used.
  - Displays the timestamp of the last session.
  - Summarizes correct vs incorrect answers.
  - Provides a link to the group.

- **Study Progress**
  - Displays total words studied across all study sessions (e.g., `3/124`).
  - Shows overall mastery progress as a percentage.

- **Quick Stats**
  - Success rate (e.g., `80%`)
  - Total study sessions (e.g., `4`)
  - Total active groups (e.g., `3`)
  - Study streak (e.g., `4 days`)

- **Start Studying Button**
  - Redirects to the study activities page.

#### Required API Endpoints

- `GET /api/dashboard/last_study_session`
- `GET /api/dashboard/study_progress`
- `GET /api/dashboard/quick_stats`

---

### Study Activities Index `/study_activities`

#### Purpose

This page displays a collection of study activities with thumbnails and names to either launch or view the study activity.

#### Components

- **Study Activity Card**
  - Thumbnail of the study activity.
  - Name of the study activity.
  - Button to launch the activity.
  - Button to view past study sessions for this activity.

#### Required API Endpoints

- `GET /api/study_activities`

---

### Study Activity Details `/study_activities/:id`

#### Purpose

This page shows details of a study activity and its past study sessions.

#### Components

- Study activity name
- Thumbnail
- Description
- Launch button
- Paginated list of past study sessions

#### Required API Endpoints

- `GET /api/study_activities/:id`
- `GET /api/study_activities/:id/study_sessions`

---

### Study Activity Launch `/study_activities/:id/launch`

#### Purpose

This page allows the user to launch a study activity.

#### Components

- Study activity name
- Launch form
  - Select field for group
  - Launch now button

#### Required API Endpoints

- `POST /api/study_activities`

---

### Words Index `/words`

#### Purpose

This page displays all words available in the database.

#### Components

- **Paginated Word List**
  - JSON Format:

    ```json
    {
      "hangul":"학교",
      "romanization":"hakgyo",
      "type":"noun",
      "english":[
          "school"
      ],
      "example_sentence":{
          "korean":"그는 학교에서 저보다 한 학년 위였어요.",
          "english":"He was a year ahead of me in school."
      },
      "correct_count": 10,
      "wrong_count": 2
    }
    ```

  - Paginated (100 words per page).
  - Clicking a word redirects to the word details page.

#### Required API Endpoints

- `GET /api/words`

---

### Word Details `/words/:id`

#### Purpose

This page provides detailed information about a specific word.

#### Components

- JSON Format:

  ```json
  {
    "id": 5,
    "word": {
    "hangul": "학생",
    "romanization": "haksaeng",
    "english": ["student"],  
    "example_sentence": {
      "korean": "이 학생은 공부를 열심히 합니다.",
      "english": "This student studies hard."
  },
  }
    "study_statistics": {
      "correct_count": 5,
      "wrong_count": 1
    },
  }
  ```

#### Required API Endpoints

- `GET /api/words/:id`

---

### Sentence Practice `/sentence_practice`

#### Purpose

This page allows users to practice constructing sentences using Korean vocabulary, similar to word practice.

#### Components

- **Sentence Construction Tool**
  - Displays a sentence in English that the user must translate into Korean.
  - Provides a selection of words that can be dragged and dropped to form the sentence.
  - Provides feedback on correctness with possible alternative translations.
  - Tracks correct and incorrect sentence attempts.

- **Example Sentences**
  - Displays example sentences with translations for reference.
  - Allows users to attempt translation and compare with model answers.

#### Required API Endpoints

- `GET /api/sentence_practice`
  - Retrieves random sentences for practice from data_korean.json.
  - Example Response:

  ```json
  {
  "sentence_id": 12,
  "word": {
    "hangul": "학생",
    "romanization": "haksaeng",
    "english": ["student"]
  },
  "example_sentence": {
    "korean": "이 학생은 공부를 열심히 합니다.",
    "english": "This student studies hard."
  }
  }
  ```

- `POST /api/sentence_practice/attempt` (Submits user's sentence attempt for evaluation)
  - Submits a user's attempt at translating a sentence.
  - Example Request:

```json
{
"sentence_id": 12,
"user_translation": "이 학생은 공부를 열심히 합니다."
}

```

- Example Response:

```json
{
  "correct": true,
  "message": "Correct! Well done!",
  "alternatives": ["이 학생은 정말 열심히 공부해요."]
}
```

- `GET /api/sentence_practice/examples` (Retrieves example sentences for learning)
  - Fetches example sentences for a given word.
  - Example Request: /api/sentence_practice/examples?word=학생
  
  - Example Response:

```json
{
"word": "학생",
"example_sentences": [
  {
    "korean": "이 학생은 공부를 열심히 합니다.",
    "english": "This student studies hard."
  },
  {
    "korean": "학생들은 도서관에서 공부하고 있어요.",
    "english": "The students are studying in the library."
  }
]
}
```

- GET /api/sentence_practice/statistics
Retrieves the user's progress in sentence practice.
Example Response:

```json
{
  "total_sentences_attempted": 50,
  "correct_answers": 40,
  "accuracy_rate": "80%"
}
```

---

### Groups Index `/groups`

#### Purpose

This page displays a list of word groups in the database.

#### Components

- **Paginated Group List**
  - JSON Format:

    ```json
    {
      "id": 1,
      "group_name": "School-related Words",
      "word_count": 15
    }
    ```

#### Required API Endpoints

- `GET /api/groups`

---

### Group Details `/groups/:id`

#### Purpose

This page shows details of a specific group, including words and study sessions associated with it.

#### Components

- JSON Format:

  ```json
  {
    "group_name": "School-related Words",
    "total_word_count": 15,
    "words": [
      {"hangul": "학교", "romanization": "hakgyo", "english": ["school"]},
      {"hangul": "학생", "romanization": "haksaeng", "english": ["student"]}
    ]
  }
  ```

#### Required API Endpoints

- `GET /api/groups/:id`
- `GET /api/groups/:id/words`
- `GET /api/groups/:id/study_sessions`

### Settings Page `/settings`

#### Purpose

This page allows users to configure study portal settings.

#### Components

- **Theme Selection**
  - Light, Dark, or System Default theme selection.
- **Reset History Button**
  - Deletes all study sessions and word review items.
- **Full Reset Button**
  - Drops all tables and re-creates the database with seed data.

#### Required API Endpoints

- `POST /api/reset_history`
- `POST /api/full_reset`

---
