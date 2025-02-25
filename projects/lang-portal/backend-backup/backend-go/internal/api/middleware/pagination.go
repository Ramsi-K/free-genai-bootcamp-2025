package middleware

import (
	"strconv"
)

type Pagination struct {
	Page   string `form:"page"`
	SortBy string `form:"sort_by"`
	Order  string `form:"order"`
	limit  int
}

// Validate checks if pagination parameters are valid
func (p *Pagination) Validate() error {
	if p.Page != "" {
		if _, err := strconv.Atoi(p.Page); err != nil {
			return err
		}
	}
	return nil
}

func (p *Pagination) GetPage() int {
	page, err := strconv.Atoi(p.Page)
	if err != nil || page < 1 {
		return 1
	}
	return page
}

func (p *Pagination) GetLimit() int {
	if p.limit == 0 {
		p.limit = 10 // Default limit
	}
	return p.limit
}

func (p *Pagination) GetOrder() string {
	if p.Order != "desc" {
		return "asc"
	}
	return "desc"
}

// SetLimit allows setting a custom limit for testing
func (p *Pagination) SetLimit(limit int) {
	p.limit = limit
}
