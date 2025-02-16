package handlers

import (
    "net/http"
    "github.com/gin-gonic/gin"
    "gorm.io/gorm"
    "github.com/yourusername/lang-portal/internal/models"
    "github.com/yourusername/lang-portal/internal/api/middleware"
)

type WordHandler struct {
    db *gorm.DB
}

func NewWordHandler(db *gorm.DB) *WordHandler {
    return &WordHandler{db: db}
}

func (h *WordHandler) List(c *gin.Context) {
    var pagination middleware.Pagination
    if err := c.ShouldBindQuery(&pagination); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }

    var words []models.Word
    query := h.db.Model(&models.Word{})

    // Apply sorting
    if pagination.SortBy != "" {
        order := pagination.SortBy + " " + pagination.GetOrder()
        query = query.Order(order)
    }

    // Apply pagination
    query = query.Offset(pagination.GetOffset()).Limit(pagination.GetLimit())

    if err := query.Find(&words).Error; err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": "Error fetching words"})
        return
    }

    // Format response
    response := make([]gin.H, len(words))
    for i, word := range words {
        response[i] = gin.H{
            "id":           word.ID,
            "hangul":       word.Hangul,
            "romanization": word.Romanization,
            "english":      word.English,
            "type":         word.Type,
            "example": gin.H{
                "korean":  word.ExampleKorean,
                "english": word.ExampleEnglish,
            },
        }
    }

    c.JSON(http.StatusOK, response)
}

func (h *WordHandler) Get(c *gin.Context) {
    id := c.Param("id")
    var word models.Word

    if err := h.db.First(&word, id).Error; err != nil {
        if err == gorm.ErrRecordNotFound {
            c.JSON(http.StatusNotFound, gin.H{"error": "Word not found"})
            return
        }
        c.JSON(http.StatusInternalServerError, gin.H{"error": "Error fetching word"})
        return
    }

    c.JSON(http.StatusOK, gin.H{
        "id":           word.ID,
        "hangul":       word.Hangul,
        "romanization": word.Romanization,
        "english":      word.English,
        "type":         word.Type,
        "example": gin.H{
            "korean":  word.ExampleKorean,
            "english": word.ExampleEnglish,
        },
    })
} 