# Lang Portal Backend (Python + Flask)

This is the backend for Lang Portal, a Korean vocabulary learning platform. It is built using **Flask** and **SQLite3**.

## 📜 Full Backend Specifications

For a complete description of the backend structure, database schema, and API endpoints, see:  
➡️ **[`backend-technical-specs-Python-Flask.md`](backend-technical-specs-Python-Flask.md)**

## 🚀 Quick Setup

### 1️⃣ Install Dependencies

```sh
pip install -r requirements.txt
```

### 2️⃣ Initialize the Database

```sh
invoke init-db
```

### 3️⃣ Run the Backend API

```sh
python app.py
```

## ⚡ Using Cursor AI

Cursor AI will use the **backend specs file** to implement missing functionality.

## Setting up the database

```sh
invoke init-db
```

This will do the following:

- create the words.db (Sqlite3 database)
- run the migrations found in `seeds/`
- run the seed data found in `seed/`

Please note that migrations and seed data is manually coded to be imported in the `lib/db.py`. So you need to modify this code if you want to import other seed data.

## Clearing the database

Simply delete the `words.db` to clear entire database.

## Running the backend api

```sh
python app.py 
```

This should start the flask app on port `5000`

## 📂 Backend Directory Structure

.
├── app.py              # Main entry point
├── db.py               # Database connection & setup
├── routes/             # API routes
│   ├── words.py        # Words API
│   ├── groups.py       # Groups API
│   ├── study_sessions.py  # Study sessions API
│   ├── study_activities.py  # Study activities API
│   ├── dashboard.py    # Dashboard API
├── sql/                # Database migrations
│   ├── setup/          # Table creation SQL scripts
├── seed/               # JSON seed data
│   ├── data_korean.json # Korean vocabulary words
│   ├── study_activities.json # Study activities
├── requirements.txt    # Python dependencies
├── README.md           # This file
