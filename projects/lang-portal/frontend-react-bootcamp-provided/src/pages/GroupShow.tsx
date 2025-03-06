import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { 
  fetchGroupDetails, 
  fetchGroupStudySessions, 
  fetchGroupWords,
  type GroupDetails, 
  type StudySession,
  type StudySessionSortKey,
  type Word 
} from '../services/api'
import WordsTable, { type WordSortKey } from '../components/WordsTable'
import StudySessionsTable from '../components/StudySessionsTable'
import Pagination from '../components/Pagination'
import { useNavigation } from '../context/NavigationContext'

export default function GroupShow() {
  const { id } = useParams<{ id: string }>()
  const [group, setGroup] = useState<GroupDetails | null>(null)
  const { setCurrentGroup } = useNavigation()
  const [words, setWords] = useState<Word[]>([])
  const [studySessions, setStudySessions] = useState<StudySession[]>([])
  const [wordSortKey, setWordSortKey] = useState<WordSortKey>('kanji')
  const [wordSortDirection, setWordSortDirection] = useState<'asc' | 'desc'>('asc')
  const [sessionSortKey, setSessionSortKey] = useState<StudySessionSortKey>('startTime')
  const [sessionSortDirection, setSessionSortDirection] = useState<'asc' | 'desc'>('desc')
  const [wordsPage, setWordsPage] = useState(1)
  const [sessionsPage, setSessionsPage] = useState(1)
  const [wordsTotalPages, setWordsTotalPages] = useState(1)
  const [sessionsTotalPages, setSessionsTotalPages] = useState(1)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadData = async () => {
      if (!id) return
      
      setIsLoading(true)
      setError(null)
      try {
        const groupData = await fetchGroupDetails(parseInt(id, 10))
        setGroup(groupData)
        setCurrentGroup(groupData)
        
        const [wordsData, sessionsData] = await Promise.all([
          fetchGroupWords(
            parseInt(id, 10),
            wordsPage,
            wordSortKey,
            wordSortDirection
          ),
          fetchGroupStudySessions(
            parseInt(id, 10),
            sessionsPage,
            sessionSortKey,
            sessionSortDirection
          )
        ])
        
        setWords(wordsData.words)
        setWordsTotalPages(wordsData.total_pages)
        setStudySessions(sessionsData.study_sessions)
        setSessionsTotalPages(sessionsData.total_pages)
      } catch (err) {
        setError('Failed to load group details')
        console.error(err)
      } finally {
        setIsLoading(false)
      }
    }

    loadData()
  }, [id, wordsPage, sessionsPage, wordSortKey, wordSortDirection, sessionSortKey, sessionSortDirection, setCurrentGroup])

  // Clean up the context when unmounting
  useEffect(() => {
    return () => {
      setCurrentGroup(null)
    }
  }, [setCurrentGroup])

  const handleWordSort = (key: WordSortKey) => {
    if (key === wordSortKey) {
      setWordSortDirection(wordSortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setWordSortKey(key)
      setWordSortDirection('asc')
    }
  }

  const handleSessionSort = (key: StudySessionSortKey) => {
    if (key === sessionSortKey) {
      setSessionSortDirection(sessionSortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSessionSortKey(key)
      setSessionSortDirection('asc')
    }
  }

  if (isLoading) {
    return <div className="text-center py-4">Loading...</div>
  }

  if (error || !group) {
    return <div className="text-red-500 text-center py-4">{error || 'Group not found'}</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800 dark:text-white">{group.group_name}</h1>
        <Link
          to="/groups"
          className="px-4 py-2 text-sm font-medium text-gray-600 bg-gray-100 rounded-md hover:bg-gray-200 dark:text-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600"
        >
          Back to Groups
        </Link>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        <div className="p-6">
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-gray-800 dark:text-white">Group Statistics</h2>
            <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="grid grid-cols-1 gap-4">
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Total Words</p>
                  <p className="mt-1 text-2xl font-semibold text-blue-500">{group.word_count}</p>
                </div>
              </div>
            </div>
          </div>

          <div className="mb-8">
            <h2 className="text-lg font-semibold text-gray-800 dark:text-white mb-4">Words in Group</h2>
            <WordsTable
              words={words}
              sortKey={wordSortKey}
              sortDirection={wordSortDirection}
              onSort={handleWordSort}
            />
            <Pagination
              currentPage={wordsPage}
              totalPages={wordsTotalPages}
              onPageChange={setWordsPage}
            />
          </div>

          <div>
            <h2 className="text-lg font-semibold text-gray-800 dark:text-white mb-4">Study Sessions</h2>
            <StudySessionsTable
              sessions={studySessions}
              sortKey={sessionSortKey}
              sortDirection={sessionSortDirection}
              onSort={handleSessionSort}
            />
            <Pagination
              currentPage={sessionsPage}
              totalPages={sessionsTotalPages}
              onPageChange={setSessionsPage}
            />
          </div>
        </div>
      </div>
    </div>
  )
}