import React, { useState, useEffect } from 'react'
import StudySessionsTable, { type StudySessionSortKey } from '../components/StudySessionsTable'
import Pagination from '../components/Pagination'
import { type StudySession, fetchStudySessions } from '../services/api'

export default function Sessions() {
  const [sessions, setSessions] = useState<StudySession[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [sortKey, setSortKey] = useState<StudySessionSortKey>('startTime')
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc')
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const itemsPerPage = 10

  useEffect(() => {
    const loadSessions = async () => {
      try {
        setLoading(true)
        const response = await fetchStudySessions(currentPage, itemsPerPage)
        setSessions(response.items)
        setTotalPages(response.total_pages)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load sessions')
      } finally {
        setLoading(false)
      }
    }

    loadSessions()
  }, [currentPage])

  const handleSort = (key: StudySessionSortKey) => {
    if (key === sortKey) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortKey(key)
      setSortDirection('asc')
    }
  }

  if (loading) {
    return <div className="text-center py-4">Loading...</div>
  }

  if (error) {
    return <div className="text-red-500 text-center py-4">{error}</div>
  }

  const sortedSessions = [...sessions].sort((a, b) => {
    const aValue = a[sortKey.toLowerCase() as keyof StudySession]
    const bValue = b[sortKey.toLowerCase() as keyof StudySession]
    if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1
    if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1
    return 0
  })

  const paginatedSessions = sortedSessions.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  )

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-gray-800 dark:text-white">Study Sessions</h1>
      <StudySessionsTable
        sessions={paginatedSessions}
        sortKey={sortKey}
        sortDirection={sortDirection}
        onSort={handleSort}
      />
      {totalPages > 1 && (
        <div className="flex justify-between items-center">
          <button
            onClick={() => setCurrentPage(currentPage - 1)}
            disabled={currentPage === 1}
            className="px-4 py-2 font-medium text-gray-600 bg-gray-100 rounded-md hover:bg-gray-200 dark:text-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          <span className="text-gray-600 dark:text-gray-300">
            Page <span className="font-bold">{currentPage}</span> of {totalPages}
          </span>
          <button
            onClick={() => setCurrentPage(currentPage + 1)}
            disabled={currentPage === totalPages}
            className="px-4 py-2 font-medium text-gray-600 bg-gray-100 rounded-md hover:bg-gray-200 dark:text-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      )}
    </div>
  )
}