package router

import (
	"github.com/Ramsi-K/free-genai-bootcamp-2025/projects/lang-portal/backend-go/internal/api/handlers"
	"github.com/Ramsi-K/free-genai-bootcamp-2025/projects/lang-portal/backend-go/internal/api/middleware"
	"github.com/gin-gonic/gin"
	"gorm.io/gorm"
)

func SetupRouter(db *gorm.DB) *gin.Engine {
	r := gin.Default()

	// Enable CORS
	r.Use(middleware.CORS())

	// Create handlers
	wordHandler := handlers.NewWordHandler(db)
	groupHandler := handlers.NewGroupHandler(db)
	studyActivityHandler := handlers.NewStudyActivityHandler(db)
	dashboardHandler := handlers.NewDashboardHandler(db)
	settingsHandler := handlers.NewSettingsHandler(db)
	sentencePracticeHandler := handlers.NewSentencePracticeHandler(db)

	// API routes
	api := r.Group("/api")
	{
		// Dashboard endpoints
		dashboard := api.Group("/dashboard")
		{
			dashboard.GET("/last_study_session", dashboardHandler.GetLastStudySession)
			dashboard.GET("/study_progress", dashboardHandler.GetStudyProgress)
			dashboard.GET("/quick_stats", dashboardHandler.GetQuickStats)
		}

		// Words endpoints
		words := api.Group("/words")
		{
			words.GET("", wordHandler.List)
			words.GET("/:id", wordHandler.Get)
		}

		// Groups endpoints
		groups := api.Group("/groups")
		{
			groups.GET("", groupHandler.List)
			groups.GET("/:id", groupHandler.Get)
			groups.GET("/:id/words", groupHandler.GetWords)
			groups.GET("/:id/study_sessions", groupHandler.GetStudySessions)
		}

		// Study activities endpoints
		activities := api.Group("/study_activities")
		{
			activities.GET("", studyActivityHandler.List)
			activities.GET("/:id", studyActivityHandler.Get)
			activities.GET("/:id/study_sessions", studyActivityHandler.GetSessions)
			activities.POST("", studyActivityHandler.Create)
			activities.POST("/:id/launch", studyActivityHandler.Launch)
		}

		// Sentence practice endpoints
		sentencePractice := api.Group("/sentence_practice")
		{
			sentencePractice.GET("", sentencePracticeHandler.GetPracticeSentence)
			sentencePractice.POST("/attempt", sentencePracticeHandler.SubmitSentenceAttempt)
			sentencePractice.GET("/examples", sentencePracticeHandler.GetSentenceExamples)
			sentencePractice.GET("/statistics", sentencePracticeHandler.GetSentenceStatistics)
		}

		// Settings endpoints
		settings := api.Group("/settings")
		{
			settings.POST("/reset_history", settingsHandler.ResetHistory)
			settings.POST("/full_reset", settingsHandler.FullReset)
		}
	}

	return r
}
