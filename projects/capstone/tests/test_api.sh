#!/bin/bash

# --- Configuration ---
# Use the service name 'api' within Docker
API_BASE_URL="${API_BASE_URL:-http://localhost:8000/api}"
HEALTH_URL="${API_BASE_URL%api}health" # Health endpoint is on localhost:8000
export API_BASE_URL
export HEALTH_URL

# --- Helper Functions ---

# Function to send a GET request and check the response
test_get() {
  local url="$1"
  local description="$2"
  local expected_status="$3"

  echo -e "\n🔍 Testing GET $url - $description"
  local code=$(curl -s -o /dev/null -w "%{http_code}" "$url")
  if [[ "$code" -eq "$expected_status" ]]; then
    echo -e "✅ \033[32mPASS\033[0m $url [$code]"
  else
    echo -e "❌ \033[31mFAIL\033[0m $url → $code (Expected $expected_status)"
    return 1
  fi
}

# Function to send a POST request and check the response
test_post() {
  local endpoint="$1"
  local data="$2"
  local description="$3"
  local expected_status="$4"

  echo -e "\n📤 Testing POST $endpoint - $description"
  local code=$(curl -s -o /dev/null -w "%{http_code}" -H "Content-Type: application/json" -X POST -d "$data" "$API_BASE_URL/$endpoint")
  if [[ "$code" -eq "$expected_status" ]]; then
    echo -e "✅ \033[32mPASS\033[0m $endpoint [$code]"
  else
    echo -e "❌ \033[31mFAIL\033[0m $endpoint → $code (Expected $expected_status)"
    return 1
  fi
}

# Function to send a PUT request and check the response
test_put() {
  local endpoint="$1"
  local data="$2"
  local description="$3"
  local expected_status="$4"

  echo -e "\n🔁 Testing PUT $endpoint - $description"
  local code=$(curl -s -o /dev/null -w "%{http_code}" -H "Content-Type: application/json" -X PUT -d "$data" "$API_BASE_URL/$endpoint")
  if [[ "$code" -eq "$expected_status" ]]; then
    echo -e "✅ \033[32mPASS\033[0m $endpoint [$code]"
  else
    echo -e "❌ \033[31mFAIL\033[0m $endpoint → $code (Expected $expected_status)"
    return 1
  fi
}

# Function to send a PATCH request and check the response
test_patch() {
  local endpoint="$1"
  local data="$2"
  local description="$3"
  local expected_status="$4"

  echo -e "\n🩹 Testing PATCH $endpoint - $description"
  local code=$(curl -s -o /dev/null -w "%{http_code}" -H "Content-Type: application/json" -X PATCH -d "$data" "$API_BASE_URL/$endpoint")
  if [[ "$code" -eq "$expected_status" ]]; then
    echo -e "✅ \033[32mPASS\033[0m $endpoint [$code]"
  else
    echo -e "❌ \033[31mFAIL\033[0m $endpoint → $code (Expected $expected_status)"
    return 1
  fi
}

# Function to send a DELETE request and check the response
test_delete() {
  local endpoint="$1"
  local description="$2"
  local expected_status="$3"

  echo -e "\n🗑️ Testing DELETE $endpoint - $description"
  local code=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$API_BASE_URL/$endpoint")
  if [[ "$code" -eq "$expected_status" ]]; then
    echo -e "✅ \033[32mPASS\033[0m $endpoint [$code]"
  else
    echo -e "❌ \033[31mFAIL\033[0m $endpoint → $code (Expected $expected_status)"
    return 1
  fi
}

# --- Real Endpoint Tests ---

# Function to reset the database
reset_database() {
  echo -e "\n🔄 Resetting the database..."
  local code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_BASE_URL/admin/reset/all")
  if [[ "$code" -eq 200 ]]; then
    echo -e "✅ \033[32mPASS\033[0m Database reset [$code]"
  else
    echo -e "❌ \033[31mFAIL\033[0m Database reset → $code (Expected 200)"
  fi
}


# Health Check (Special Case)
test_get "$HEALTH_URL" "Check if the API is healthy" 200

# Words
test_get "$API_BASE_URL/words" "List all words" 200
test_get "$API_BASE_URL/words/1" "Get word by ID" 200
test_post "words" '{"korean": "테스트", "english": "test"}' "Create word" 201
test_put "words/1" '{"korean": "수정됨", "english": "edited"}' "Update word" 200
test_delete "words/1" "Delete word" 200
test_get "words/1/sentences" "Get word sentences" 200
test_post "words/1/sentences" '{"sentence_korean": "예시 문장", "sentence_english": "example"}' "Add sentence" 200
test_get "words/1/stats" "Get word stats" 200
test_patch "words/1/stats" '{"times_seen": 3}' "Update stats" 200

# Groups
test_get "$API_BASE_URL/groups" "List all groups" 200
test_get "$API_BASE_URL/groups/1" "Get group by ID" 200
test_post "groups" '{"name": "테스트 그룹", "description": "예시 설명"}' "Create group" 201
test_put "groups/1" '{"name": "수정된 그룹", "description": "수정"}' "Update group" 200
test_delete "groups/1" "Delete group" 200
test_get "groups/1/words" "Get group words" 200
test_post "groups/1/words" '{"word_ids": [2,3]}' "Add multiple words" 201
test_post "groups/1/add-word/2" '{}' "Add word to group" 200
test_delete "groups/1/remove-word/2" "Remove word from group" 200
test_get "groups/1/study_sessions" "Get group study sessions" 200

# Study Sessions
test_get "$API_BASE_URL/study_sessions" "List all study sessions" 200
test_get "$API_BASE_URL/study_sessions/1" "Get study session by ID" 200
test_post "study_sessions" '{"group_id": 1, "user_id": 1, "start_time": "2023-01-01T00:00:00Z", "end_time": "2023-01-01T01:00:00Z"}' "Create study session" 201
test_put "study_sessions/1" '{"end_time": "2023-01-01T02:00:00Z"}' "Update study session" 200
test_delete "study_sessions/1" "Delete study session" 200

# Study Activities
test_get "$API_BASE_URL/study_activities" "List all study activities" 200
test_get "$API_BASE_URL/study_activities/1" "Get study activity by ID" 200
test_post "study_activities" '{"study_session_id": 1, "activity_type": "listening", "duration": 30}' "Create study activity" 201
test_put "study_activities/1" '{"duration": 45}' "Update study activity" 200
test_delete "study_activities/1" "Delete study activity" 200

# Mistakes
test_get "$API_BASE_URL/mistakes" "List all mistakes" 200
test_get "$API_BASE_URL/mistakes/1" "Get mistake by ID" 200
test_post "mistakes" '{"word_id": 1, "user_id": 1, "mistake_type": "pronunciation", "details": "Incorrect pronunciation"}' "Create mistake" 201
test_put "mistakes/1" '{"details": "Corrected pronunciation"}' "Update mistake" 200
test_delete "mistakes/1" "Delete mistake" 200

# Activity Logs
test_get "$API_BASE_URL/activity_logs" "List all activity logs" 200
test_get "$API_BASE_URL/activity_logs/1" "Get activity log by ID" 200
test_post "activity_logs" '{"user_id": 1, "activity_type": "login", "timestamp": "2023-01-01T00:00:00Z"}' "Create activity log" 201
test_put "activity_logs/1" '{"activity_type": "logout"}' "Update activity log" 200
test_delete "activity_logs/1" "Delete activity log" 200

# Admin
test_get "$API_BASE_URL/admin/users" "List all users" 200
test_get "$API_BASE_URL/admin/users/1" "Get user by ID" 200
test_post "admin/users" '{"username": "testuser", "email": "test@example.com", "password": "password123"}' "Create user" 201
test_put "admin/users/1" '{"email": "updated@example.com"}' "Update user" 200
test_delete "admin/users/1" "Delete user" 200

# Dashboard
test_get "$API_BASE_URL/dashboard/overview" "Get dashboard overview" 200
test_get "$API_BASE_URL/dashboard/user_progress/1" "Get user progress" 200
test_get "$API_BASE_URL/dashboard/group_progress/1" "Get group progress" 200

# Session Stats
test_get "$API_BASE_URL/session_stats" "List all session stats" 200
test_get "$API_BASE_URL/session_stats/1" "Get session stats by ID" 200
test_post "session_stats" '{"study_session_id": 1, "correct_count": 10, "incorrect_count": 2}' "Create session stats" 201
test_put "session_stats/1" '{"correct_count": 15}' "Update session stats" 200
test_delete "session_stats/1" "Delete session stats" 200

# Word Review Items
test_get "$API_BASE_URL/word_review_items" "List all word review items" 200
test_get "$API_BASE_URL/word_review_items/1" "Get word review item by ID" 200
test_post "word_review_items" '{"word_id": 1, "user_id": 1, "review_date": "2023-01-01T00:00:00Z"}' "Create word review item" 201
test_put "word_review_items/1" '{"review_date": "2023-01-02T00:00:00Z"}' "Update word review item" 200
test_delete "word_review_items/1" "Delete word review item" 200

# Wrong Inputs
test_get "$API_BASE_URL/wrong_inputs" "List all wrong inputs" 200
test_get "$API_BASE_URL/wrong_inputs/1" "Get wrong input by ID" 200
test_post "wrong_inputs" '{"word_id": 1, "user_id": 1, "input": "잘못된 입력"}' "Create wrong input" 201
test_put "wrong_inputs/1" '{"input": "수정된 입력"}' "Update wrong input" 200
test_delete "wrong_inputs/1" "Delete wrong input" 200

# Reset the database after all tests
reset_database
