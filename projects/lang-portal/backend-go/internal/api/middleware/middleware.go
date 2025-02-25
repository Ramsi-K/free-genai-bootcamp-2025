package middleware

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

// ErrorResponse represents a standardized error response
type ErrorResponse struct {
	Status  int    `json:"status"`
	Message string `json:"message"`
}

// ErrorHandler middleware handles errors and formats them consistently
func ErrorHandler() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Next()

		if len(c.Errors) > 0 {
			err := c.Errors.Last()
			c.JSON(http.StatusInternalServerError, ErrorResponse{
				Status:  http.StatusInternalServerError,
				Message: err.Error(),
			})
			return
		}
	}
}

// ResponseFormatter middleware ensures consistent response format
func ResponseFormatter() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Next()

		// Skip if response is already written or there are errors
		if c.Writer.Written() || len(c.Errors) > 0 {
			return
		}

		// Get the response data
		data := c.Keys["response"]
		if data == nil {
			return
		}

		// Format the response
		c.JSON(http.StatusOK, gin.H{
			"status": http.StatusOK,
			"data":   data,
		})
	}
}

// RequestValidator middleware validates request parameters
func RequestValidator() gin.HandlerFunc {
	return func(c *gin.Context) {
		// Add validation logic here based on the endpoint
		// For example, validate pagination parameters
		if page := c.Query("page"); page != "" {
			if page == "0" {
				c.AbortWithStatusJSON(http.StatusBadRequest, ErrorResponse{
					Status:  http.StatusBadRequest,
					Message: "Page number must be greater than 0",
				})
				return
			}
		}

		if limit := c.Query("limit"); limit != "" {
			if limit == "0" {
				c.AbortWithStatusJSON(http.StatusBadRequest, ErrorResponse{
					Status:  http.StatusBadRequest,
					Message: "Limit must be greater than 0",
				})
				return
			}
		}

		c.Next()
	}
}
