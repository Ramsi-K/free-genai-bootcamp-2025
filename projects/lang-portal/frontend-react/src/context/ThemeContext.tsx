import React, { createContext, useContext, useState, useEffect } from 'react'

type Theme = 'light' | 'dark' | 'system'

type ThemeContextType = {
  theme: Theme
  setTheme: (theme: Theme) => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

const isValidTheme = (theme: string | null): theme is Theme => {
  return theme === 'light' || theme === 'dark' || theme === 'system'
}

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setTheme] = useState<Theme>(() => {
    const savedTheme = localStorage.getItem('theme')
    return isValidTheme(savedTheme) ? savedTheme : 'system'
  })

  const updateTheme = (newTheme: Theme) => {
    const root = document.documentElement
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    
    // Remove both classes first
    root.classList.remove('light', 'dark')

    // Determine which theme to apply
    if (newTheme === 'system') {
      root.classList.add(systemPrefersDark ? 'dark' : 'light')
    } else {
      root.classList.add(newTheme)
    }
  }

  // Initial theme setup
  useEffect(() => {
    updateTheme(theme)
  }, [])

  // Effect for handling theme changes
  useEffect(() => {
    updateTheme(theme)
    localStorage.setItem('theme', theme)
  }, [theme])

  // Effect for handling system theme changes
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    
    const handleChange = () => {
      if (theme === 'system') {
        updateTheme('system')
      }
    }

    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [theme])

  const handleSetTheme = (newTheme: Theme) => {
    setTheme(newTheme)
    localStorage.setItem('theme', newTheme)
  }

  return (
    <ThemeContext.Provider value={{ theme, setTheme: handleSetTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

export const useTheme = () => {
  const context = useContext(ThemeContext)
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}