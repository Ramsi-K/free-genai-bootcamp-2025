# Diagrams

## Entity Relationship Diagram

``` mermaid
erDiagram
    WORDS {
        int id PK
        string japanese
        string romaji
        string english
        json parts
    }
    
    WORDS_GROUPS {
        int id PK
        int word_id FK
        int group_id FK
    }
    
    GROUPS {
        int id PK
        string name
    }
    
    STUDY_SESSIONS {
        int id PK
        int group_id FK
        int study_activity_id FK
        datetime created_at
    }
    
    STUDY_ACTIVITIES {
        int id PK
        string name
    }
    
    WORD_REVIEW_ITEMS {
        int word_id FK
        int study_session_id FK
        boolean correct
        datetime created_at
    }
    
    WORDS ||--o{ WORDS_GROUPS : has
    GROUPS ||--o{ WORDS_GROUPS : has
    GROUPS ||--o{ STUDY_SESSIONS : contains
    STUDY_SESSIONS ||--|{ WORD_REVIEW_ITEMS : records
    STUDY_ACTIVITIES ||--o{ STUDY_SESSIONS : contains
    WORDS ||--|{ WORD_REVIEW_ITEMS : reviewed_in
```

---

## System Architecture Diagram

``` mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Database

    User->>Frontend: Navigate to Dashboard
    Frontend->>Backend: GET /api/dashboard/last_study_session
    Backend->>Database: Fetch latest study session
    Database-->>Backend: Return session data
    Backend-->>Frontend: JSON Response
    Frontend-->>User: Display Dashboard Data

    User->>Frontend: View Study Activities
    Frontend->>Backend: GET /api/study_activities
    Backend->>Database: Fetch available study activities
    Database-->>Backend: Return study activities data
    Backend-->>Frontend: JSON Response
    Frontend-->>User: Display Study Activities List

    User->>Frontend: Start a Study Session
    Frontend->>Backend: POST /api/study_activities
    Backend->>Database: Create new study session
    Database-->>Backend: Confirm study session created
    Backend-->>Frontend: JSON Response
    Frontend-->>User: Launch Study Session

    User->>Frontend: View Word Details
    Frontend->>Backend: GET /api/words/:id
    Backend->>Database: Fetch word details and stats
    Database-->>Backend: Return word data
    Backend-->>Frontend: JSON Response
    Frontend-->>User: Display Word Details

    User->>Frontend: View Groups
    Frontend->>Backend: GET /api/groups
    Backend->>Database: Fetch groups data
    Database-->>Backend: Return groups
    Backend-->>Frontend: JSON Response
    Frontend-->>User: Display Groups
```

---

## Component Diagram

``` mermaid
classDiagram
    class User {
        +Interacts with UI
    }
    
    class Frontend {
        +DashboardPage
        +StudyActivitiesPage
        +StudyActivityShowPage
        +WordIndexPage
        +WordShowPage
        +GroupIndexPage
        +GroupShowPage
        +StudySessionsPage
        +StudySessionShowPage
        +SettingsPage
    }
    
    class Backend {
        +Handles API Requests
        +Processes Business Logic
        +Communicates with Database
    }
    
    class Database {
        +Stores Words, Groups, Study Sessions, and Reviews
    }
    
    User --> Frontend : Uses
    Frontend --> Backend : Sends API Requests
    Backend --> Database : Queries Data

    Frontend --> DashboardPage : Loads Dashboard Data
    Frontend --> StudyActivitiesPage : Lists Study Activities
    Frontend --> StudyActivityShowPage : Shows Study Activity Details
    Frontend --> WordIndexPage : Lists Words
    Frontend --> WordShowPage : Shows Word Details
    Frontend --> GroupIndexPage : Lists Groups
    Frontend --> GroupShowPage : Shows Group Details
    Frontend --> StudySessionsPage : Lists Study Sessions
    Frontend --> StudySessionShowPage : Shows Study Session Details
    Frontend --> SettingsPage : Configures Preferences
```

---

## API Flow Diagram

``` mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Database

    User->>Frontend: Interacts with UI

    Frontend->>Backend: GET /api/dashboard/last_study_session
    Backend->>Database: Fetch latest study session
    Database-->>Backend: Return session data
    Backend-->>Frontend: JSON Response
    Frontend-->>User: Display Dashboard Data

    Frontend->>Backend: GET /api/study_activities
    Backend->>Database: Fetch study activities
    Database-->>Backend: Return study activities data
    Backend-->>Frontend: JSON Response
    Frontend-->>User: Display Study Activities

    Frontend->>Backend: POST /api/study_activities
    Backend->>Database: Create new study session
    Database-->>Backend: Confirm session creation
    Backend-->>Frontend: JSON Response
    Frontend-->>User: Launch Study Session

    Frontend->>Backend: GET /api/words
    Backend->>Database: Fetch words data
    Database-->>Backend: Return words
    Backend-->>Frontend: JSON Response
    Frontend-->>User: Display Words List

    Frontend->>Backend: GET /api/groups
    Backend->>Database: Fetch groups
    Database-->>Backend: Return groups
    Backend-->>Frontend: JSON Response
    Frontend-->>User: Display Groups List

    Frontend->>Backend: GET /api/study_sessions
    Backend->>Database: Fetch study sessions
    Database-->>Backend: Return study sessions
    Backend-->>Frontend: JSON Response
    Frontend-->>User: Display Study Sessions List

    Frontend->>Backend: POST /api/reset_history
    Backend->>Database: Clear user progress
    Database-->>Backend: Confirm reset
    Backend-->>Frontend: JSON Response
    Frontend-->>User: Confirm Reset
```

---

## Deployment Architecture Diagram

``` mermaid
graph TD;
    User-->Frontend[Web App - Vite + Tailwind];
    Frontend-->|API Calls|Backend[Go API - Gin Framework];
    Backend-->|DB Queries|Database[SQLite Database];
    Backend-->|Deployed on|Server[VPS / Cloud Provider];
    Server-->|Handles Traffic|LoadBalancer[Load Balancer];
    LoadBalancer-->Backend;
    
    subgraph Hosting & Deployment
        Frontend-->Hosting[Netlify / Vercel]
        Backend-->CloudService[AWS / DigitalOcean]
        Database-->CloudStorage[S3 / Persistent Volume]
    end
```

---
