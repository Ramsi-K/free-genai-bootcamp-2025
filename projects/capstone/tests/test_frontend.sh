#!/bin/bash

# --- Configuration ---
API_BASE_URL="http://localhost:8000/api"

# --- Helper Functions ---

# Function to send a GET request and check the response
test_get_endpoint() {
  local endpoint="$1"
  local expected_status="$2"
  local description="$3"

  echo -e "\nTesting GET $endpoint: $description"
  response=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE_URL/$endpoint")
  if [[ "$response" -eq "$expected_status" ]]; then
    echo -e "\033[32mPASSED\033[0m: GET $endpoint returned status $response"
  else
    echo -e "\033[31mFAILED\033[0m: GET $endpoint returned status $response, expected $expected_status"
    return 1
  fi
}

# Function to send a POST request and check the response
test_post_endpoint() {
  local endpoint="$1"
  local data="$2"
  local expected_status="$3"
  local description="$4"

  echo -e "\nTesting POST $endpoint: $description"
  response=$(curl -s -o /dev/null -w "%{http_code}" -H "Content-Type: application/json" -X POST -d "$data" "$API_BASE_URL/$endpoint")
  if [[ "$response" -eq "$expected_status" ]]; then
    echo -e "\033[32mPASSED\033[0m: POST $endpoint returned status $response"
  else
    echo -e "\033[31mFAILED\033[0m: POST $endpoint returned status $response, expected $expected_status"
    return 1
  fi
}

# Function to get the ID of the last study session
get_last_session_id() {
  local session_id=$(curl -s "$API_BASE_URL/sessions" | jq -r '.[-1].id')
  echo "$session_id"
}

# Function to get the number of activity logs
get_activity_log_count() {
  local count=$(curl -s "$API_BASE_URL/logs" | jq '. | length')
  echo "$count"
}

# --- Test Cases ---

# 1. Simulate Starting a Study Session
echo -e "\n--- Test: Starting a Study Session ---"
# Check if there are any sessions before starting
initial_session_count=$(curl -s "$API_BASE_URL/sessions" | jq '. | length')
test_post_endpoint "sessions" '{"config_json": {"activity_type": "flashcards"}}' 201 "Start a new study session (flashcards)"

# Check if a new session was created
current_session_count=$(curl -s "$API_BASE_URL/sessions" | jq '. | length')
if [[ "$current_session_count" -gt "$initial_session_count" ]]; then
  echo -e "\033[32mPASSED\033[0m: A new study session was created."
else
  echo -e "\033[31mFAILED\033[0m: No new study session was created."
  exit 1
fi

# Get the ID of the newly created session
session_id=$(get_last_session_id)
echo "New session ID: $session_id"

# 2. Simulate Viewing a Flashcard
echo -e "\n--- Test: Viewing a Flashcard ---"
initial_log_count=$(get_activity_log_count)
test_post_endpoint "logs" "{\"session_id\": $session_id, \"word_id\": 1, \"activity_type\": \"REVIEW\", \"correct\": true, \"score\": 1}" 201 "Log viewing a flashcard"

# Check if a new log was created
current_log_count=$(get_activity_log_count)
if [[ "$current_log_count" -gt "$initial_log_count" ]]; then
  echo -e "\033[32mPASSED\033[0m: A new activity log was created."
else
  echo -e "\033[31mFAILED\033[0m: No new activity log was created."
  exit 1
fi

# 3. Simulate Starting a Munchers Session
echo -e "\n--- Test: Starting a Munchers Session ---"
# Check if there are any sessions before starting
initial_session_count=$(curl -s "$API_BASE_URL/sessions" | jq '. | length')
test_post_endpoint "sessions" '{"config_json": {"activity_type": "munchers"}}' 201 "Start a new study session (munchers)"

# Check if a new session was created
current_session_count=$(curl -s "$API_BASE_URL/sessions" | jq '. | length')
if [[ "$current_session_count" -gt "$initial_session_count" ]]; then
  echo -e "\033[32mPASSED\033[0m: A new study session was created."
else
  echo -e "\033[31mFAILED\033[0m: No new study session was created."
  exit 1
fi

# Get the ID of the newly created session
session_id=$(get_last_session_id)
echo "New session ID: $session_id"

# 4. Simulate Answering a Munchers Question
echo -e "\n--- Test: Answering a Munchers Question ---"
initial_log_count=$(get_activity_log_count)
test_post_endpoint "logs" "{\"session_id\": $session_id, \"word_id\": 2, \"activity_type\": \"MUNCHERS\", \"correct\": true, \"score\": 1}" 201 "Log answering a munchers question"

# Check if a new log was created
current_log_count=$(get_activity_log_count)
if [[ "$current_log_count" -gt "$initial_log_count" ]]; then
  echo -e "\033[32mPASSED\033[0m: A new activity log was created."
else
  echo -e "\033[31mFAILED\033[0m: No new activity log was created."
  exit 1
fi

echo -e "\n\033[32mFrontend-to-backend testing completed.\033[0m"

exit 0
