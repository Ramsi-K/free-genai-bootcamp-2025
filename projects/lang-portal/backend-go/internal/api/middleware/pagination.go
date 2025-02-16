package middleware

type Pagination struct {
    Page     int    `form:"page,default=1"`
    SortBy   string `form:"sort_by,default=hangul"`
    Order    string `form:"order,default=asc"`
    PageSize int    `form:"per_page,default=100"`
}

func (p *Pagination) GetOffset() int {
    return (p.Page - 1) * p.PageSize
}

func (p *Pagination) GetLimit() int {
    return p.PageSize
}

func (p *Pagination) GetOrder() string {
    if p.Order == "desc" {
        return "desc"
    }
    return "asc"
} 