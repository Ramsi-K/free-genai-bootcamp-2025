package handlers

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestStudySession_Create(t *testing.T) {
	tests := []struct {
		name           string
		payload        map[string]interface{}
		expectedStatus int
	}{
		{
			name: "Valid session creation",
			payload: map[string]interface{}{
				"group_id": 1,
			},
			expectedStatus: http.StatusOK,
		},
		{
			name: "Missing group_id",
			payload: map[string]interface{}{
				"invalid": "data",
			},
			expectedStatus: http.StatusBadRequest,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Setup
			db := createMockDB(t)
			handler := NewStudySessionHandler(db)
			router := setupTestRouter(handler)

			// Create request
			payloadBytes, _ := json.Marshal(tt.payload)
			w := httptest.NewRecorder()
			req, _ := http.NewRequest("POST", "/api/study_sessions", bytes.NewBuffer(payloadBytes))
			req.Header.Set("Content-Type", "application/json")
			router.ServeHTTP(w, req)

			// Assert status code
			assert.Equal(t, tt.expectedStatus, w.Code)

			if tt.expectedStatus == http.StatusOK {
				// Parse response
				response, err := parseResponse(w)
				assert.NoError(t, err)
				assert.NotNil(t, response["id"])
				assert.Equal(t, float64(1), response["group_id"])
			}
		})
	}
}
