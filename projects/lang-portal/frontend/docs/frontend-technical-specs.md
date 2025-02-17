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
  - id
  - activity name
  - group name
  - start time
  - end time (inferred by the last word_review_item submitted)
  - number of review items

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

#### Behaviour

After the form is submitted a new tab opens with the study activity based on its URL provided in the database.

Also the after form is submitted the page will redirect to the study sesssion show page

---

### Words Index `/words`

#### Purpose

This page displays all words available in the database.

#### Components

- **Paginated Word List**
  - JSON Format:

    ```json
    {
      "id": 1,
      "hangul": "학교",
      "romanization": "hakgyo",
      "english": "school",
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
    "english": "student",
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
      {"hangul": "학교", "romanization": "hakgyo", "english": "school"},
      {"hangul": "학생", "romanization": "haksaeng", "english": "student"}
    ]
  }
  ```

#### Required API Endpoints

- `GET /api/groups/:id`
- `GET /api/groups/:id/words`
- `GET /api/groups/:id/study_sessions`
