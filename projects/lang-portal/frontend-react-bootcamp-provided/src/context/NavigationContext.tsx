import React, { createContext, useContext, useState } from 'react'
import type { GroupDetails, Word } from '../services/api'

interface StudyActivity {
  id: number
  title: string
  launch_url: string
  preview_url: string
}

interface NavigationContextType {
  currentGroup: GroupDetails | null
  setCurrentGroup: (group: GroupDetails | null) => void
  currentWord: Word | null
  setCurrentWord: (word: Word | null) => void
  currentStudyActivity: StudyActivity | null
  setCurrentStudyActivity: (activity: StudyActivity | null) => void
}

const NavigationContext = createContext<NavigationContextType | undefined>(undefined)

export function NavigationProvider({ children }: { children: React.ReactNode }) {
  const [currentGroup, setCurrentGroup] = useState<GroupDetails | null>(null)
  const [currentWord, setCurrentWord] = useState<Word | null>(null)
  const [currentStudyActivity, setCurrentStudyActivity] = useState<StudyActivity | null>(null)

  return (
    <NavigationContext.Provider
      value={{
        currentGroup,
        setCurrentGroup,
        currentWord,
        setCurrentWord,
        currentStudyActivity,
        setCurrentStudyActivity
      }}
    >
      {children}
    </NavigationContext.Provider>
  )
}

export function useNavigation() {
  const context = useContext(NavigationContext)
  if (context === undefined) {
    throw new Error('useNavigation must be used within a NavigationProvider')
  }
  return context
}
