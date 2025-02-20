package router

import (
	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/api/handlers"
	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/api/middleware"
	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/repository"
	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/pkg/database"
	"github.com/gin-gonic/gin"
)

// SetupRouter configures all the routes for our application
func SetupRouter() *gin.Engine {
	r := gin.Default()

	// Apply global middleware
	r.Use(middleware.ErrorHandler())
	r.Use(middleware.ResponseFormatter())
	r.Use(middleware.RequestValidator())

	// Initialize repositories
	baseRepo := repository.NewBaseRepository(database.GetDB())
	wordRepo := repository.NewWordRepository(baseRepo)
	groupRepo := repository.NewGroupRepository(baseRepo)
	activityRepo := repository.NewStudyActivityRepository(baseRepo)

	// Initialize handlers
	wordHandler := handlers.NewWordHandler(wordRepo)
	groupHandler := handlers.NewGroupHandler(groupRepo)
	activityHandler := handlers.NewStudyActivityHandler(activityRepo)
	adminHandler := handlers.NewAdminHandler(database.GetDB())

	// API routes group
	api := r.Group("/api")
	{
		// Words endpoints
		api.GET("/words", wordHandler.ListWords)
		api.GET("/words/:id", wordHandler.GetWord)
		api.POST("/words/:id/correct", wordHandler.CreateCorrectStudySession)
		api.POST("/words/:id/incorrect", wordHandler.CreateIncorrectStudySession)

		// Groups endpoints
		api.GET("/groups", groupHandler.ListGroups)
		api.GET("/groups/:id", groupHandler.GetGroup)
		api.GET("/groups/:id/words", groupHandler.GetGroupWords)
		api.GET("/groups/:id/study_sessions", groupHandler.GetGroupStudySessions)

		// Dashboard endpoints
		api.GET("/dashboard/last_study_session", activityHandler.GetLastStudySession)
		api.GET("/dashboard/study_progress", activityHandler.GetStudyProgress)
		api.GET("/dashboard/quick_stats", activityHandler.GetQuickStats)

		// Study activities endpoints
		api.GET("/study_activities", activityHandler.ListActivities)
		api.GET("/study_activities/:id", activityHandler.GetActivity)
		api.POST("/study_activities", activityHandler.CreateStudySession)

		// Sentence practice endpoints
		api.GET("/sentence_practice", nil)            // TODO: Implement handler
		api.POST("/sentence_practice/attempt", nil)   // TODO: Implement handler
		api.GET("/sentence_practice/examples", nil)   // TODO: Implement handler
		api.GET("/sentence_practice/statistics", nil) // TODO: Implement handler

		// Admin endpoints
		api.POST("/admin/reset/history", adminHandler.ResetHistory)
		api.POST("/admin/reset/full", adminHandler.FullReset)
	}

	return r
}
