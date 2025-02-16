package router

import (
	"github.com/Ramsi-K/free-genai-bootcamp-2025/tree/main/projects/lang-portal/backend-go/internal/api/handlers"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"gorm.io/gorm"
)

func SetupRouter(db *gorm.DB) *gin.Engine {
	router := gin.Default()

	// Configure CORS
	router.Use(cors.Default())

	// Create handlers
	wordHandler := handlers.NewWordHandler(db)

	// Root route with API documentation
	router.GET("/", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"name":        "Korean Language Learning API",
			"version":     "1.0",
			"description": "API for managing Korean vocabulary and study sessions",
			"endpoints": gin.H{
				"words": gin.H{
					"list": "/api/words",
					"get":  "/api/words/<id>",
					"parameters": gin.H{
						"page":    "Page number (default: 1)",
						"sort_by": "Sort field (hangul, romanization, english, type)",
						"order":   "Sort order (asc, desc)",
					},
				},
				// Other endpoints will be added as we implement them
			},
		})
	})

	// API routes
	api := router.Group("/api")
	{
		// Words routes
		api.GET("/words", wordHandler.List)
		api.GET("/words/:id", wordHandler.Get)
	}

	return router
}
