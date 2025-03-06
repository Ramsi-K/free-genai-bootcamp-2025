import React, { useState, useEffect } from 'react'
import { fetchWords, type Word } from '../services/api'
import WordsTable, { WordSortKey } from '../components/WordsTable'

export default function Words() {
  const [words, setWords] = useState<Word[]>([])
  const [sortKey, setSortKey] = useState<WordSortKey>('kanji')
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc')
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadWords = async () => {
      setIsLoading(true)
      setError(null)
      try {
        const response = await fetchWords(currentPage, sortKey, sortDirection)
        setWords(response.words)
        setTotalPages(response.total_pages)
      } catch (err) {
        setError('Failed to load words')
        console.error(err)
      } finally {
        setIsLoading(false)
      }
    }

    loadWords()
  }, [currentPage, sortKey, sortDirection])

  const handleSort = (key: WordSortKey) => {
    if (key === sortKey) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortKey(key)
      setSortDirection('asc')
    }
  }

  if (isLoading) {
    return <div className="text-center py-4">Loading...</div>
  }

  if (error) {
    return <div className="text-red-500 text-center py-4">{error}</div>
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-gray-800 dark:text-white">Words</h1>
      
      <WordsTable 
        words={words}
        sortKey={sortKey}
        sortDirection={sortDirection}
        onSort={handleSort}
      />

      <div className="flex justify-center space-x-2">
        <button
          onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
          disabled={currentPage === 1}
          className="px-4 py-2 border rounded-md bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 border-gray-300 dark:border-gray-600 disabled:opacity-50 hover:bg-gray-50 dark:hover:bg-gray-700"
        >
          Previous
        </button>
        <span className="px-4 py-2 text-gray-800 dark:text-gray-200">
          Page {currentPage} of {totalPages}
        </span>
        <button
          onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
          disabled={currentPage === totalPages}
          className="px-4 py-2 border rounded-md bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 border-gray-300 dark:border-gray-600 disabled:opacity-50 hover:bg-gray-50 dark:hover:bg-gray-700"
        >
          Next
        </button>
      </div>
    </div>
  )
}