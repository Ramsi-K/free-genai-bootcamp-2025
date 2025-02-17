## Frontend Technical Spec (English - Korean JSON Format)

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
      "example":{
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
    "hangul": "학생",
    "romanization": "haksaeng",
    "english": ["student"],
    "study_statistics": {
      "correct_count": 5,
      "wrong_count": 1
    },
    "word_groups": ["학교", "교육"]
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
- `POST /api/sentence_practice/attempt` (Submits user's sentence attempt for evaluation)
- `GET /api/sentence_practice/examples` (Retrieves example sentences for learning)
- `GET /api/sentence_practice/statistics` (Retrieves user progress on sentence practice)

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
