package handlers

import (
	"net/http"

	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/models"
	"github.com/gen-ai-bootcamp-2025/lang-portal/backend-go/internal/repository"
	"github.com/gin-gonic/gin"
)

// SentencePracticeHandler handles sentence practice-related requests
type SentencePracticeHandler struct {
	wordRepo repository.WordRepository
}

// NewSentencePracticeHandler creates a new sentence practice handler instance
func NewSentencePracticeHandler(repo repository.WordRepository) *SentencePracticeHandler {
	return &SentencePracticeHandler{wordRepo: repo}
}

// GetPracticeSentence returns a random sentence for practice
func (h *SentencePracticeHandler) GetPracticeSentence(c *gin.Context) {
	// Get a random word with example sentence
	words, _, err := h.wordRepo.ListWords(1, 10)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error fetching practice sentence"})
		return
	}

	if len(words) == 0 {
		c.JSON(http.StatusNotFound, gin.H{"error": "No practice sentences available"})
		return
	}

	// Select a random word from the fetched words
	word := words[len(words)-1] // For now, just take the last one

	// Preload translations and sentences
	if err := h.wordRepo.GetDB().Preload("EnglishTranslations").Preload("Sentences").First(&word, word.ID).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error loading word details"})
		return
	}

	// Get translations
	var translations []string
	for _, t := range word.EnglishTranslations {
		translations = append(translations, t.English)
	}

	// Get first sentence if available
	var sentence models.Sentence
	if len(word.Sentences) > 0 {
		sentence = word.Sentences[0]
	}

	c.JSON(http.StatusOK, gin.H{
		"word": gin.H{
			"id":           word.ID,
			"hangul":       word.Hangul,
			"romanization": word.Romanization,
			"english":      translations,
			"type":         word.Type,
		},
		"example_sentence": gin.H{
			"korean":  sentence.Korean,
			"english": sentence.English,
		},
	})
}

// GetSentenceExamples returns example sentences for a specific word
func (h *SentencePracticeHandler) GetSentenceExamples(c *gin.Context) {
	word := c.Query("word")
	if word == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Word parameter is required"})
		return
	}

	// Find word by Hangul and preload relations
	var foundWord models.Word
	if err := h.wordRepo.GetDB().
		Preload("EnglishTranslations").
		Preload("Sentences").
		Where("hangul = ?", word).
		First(&foundWord).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Word not found"})
		return
	}

	// Get translations
	var translations []string
	for _, t := range foundWord.EnglishTranslations {
		translations = append(translations, t.English)
	}

	// Collect all example sentences
	var examples []gin.H
	for i, sentence := range foundWord.Sentences {
		examples = append(examples, gin.H{
			"korean":  sentence.Korean,
			"english": sentence.English,
			"source":  i == 0 ? "primary" : "related",
		})
	}

	// Get related words that contain this word in their sentences
	var relatedWords []models.Word
	if err := h.wordRepo.GetDB().
		Preload("Sentences").
		Joins("JOIN sentences ON sentences.word_id = words.id").
		Where("sentences.korean LIKE ?", "%"+word+"%").
		Where("words.id != ?", foundWord.ID).
		Limit(5).
		Find(&relatedWords).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error fetching examples"})
		return
	}

	// Add sentences from related words
	for _, related := range relatedWords {
		for _, sentence := range related.Sentences {
			examples = append(examples, gin.H{
				"korean":  sentence.Korean,
				"english": sentence.English,
				"source":  "related",
			})
		}
	}

	c.JSON(http.StatusOK, gin.H{
		"word": foundWord.Hangul,
		"word_info": gin.H{
			"id":           foundWord.ID,
			"hangul":       foundWord.Hangul,
			"romanization": foundWord.Romanization,
			"english":      translations,
			"type":         foundWord.Type,
		},
		"example_sentences": examples,
	})
}
