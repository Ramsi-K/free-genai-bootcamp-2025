package router

import (
    "github.com/gin-gonic/gin"
    "github.com/yourusername/lang-portal/internal/api/handlers"
    "gorm.io/gorm"
)

func SetupRouter(db *gorm.DB) *gin.Engine {
    router := gin.Default()

    // Create handlers
    wordHandler := handlers.NewWordHandler(db)

    // Root route with API documentation
    router.GET("/", func(c *gin.Context) {
        c.JSON(200, gin.H{
            "name": "Korean Language Learning API",
            "version": "1.0",
            "description": "API for managing Korean vocabulary and study sessions",
            "endpoints": gin.H{
                "words": gin.H{
                    "list": "/api/words",
                    "get": "/api/words/<id>",
                    "parameters": gin.H{
                        "page": "Page number (default: 1)",
                        "sort_by": "Sort field (hangul, romanization, english, type)",
                        "order": "Sort order (asc, desc)",
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