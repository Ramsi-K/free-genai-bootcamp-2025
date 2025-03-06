import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { fetchWordDetails, type Word } from '../services/api'
import { useNavigation } from '../context/NavigationContext'

export default function WordShow() {
  const { id } = useParams<{ id: string }>()
  const [word, setWord] = useState<Word | null>(null)
  const { setCurrentWord } = useNavigation()
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadWord = async () => {
      if (!id) return
      
      setIsLoading(true)
      setError(null)
      try {
        const wordData = await fetchWordDetails(parseInt(id, 10))
        setWord(wordData)
        setCurrentWord(wordData)
      } catch (err) {
        setError('Failed to load word details')
        console.error(err)
      } finally {
        setIsLoading(false)
      }
    }

    loadWord()
  }, [id, setCurrentWord])

  useEffect(() => {
    return () => {
      setCurrentWord(null)
    }
  }, [setCurrentWord])

  if (isLoading) {
    return <div className="text-center py-4">Loading...</div>
  }

  if (error || !word) {
    return <div className="text-red-500 text-center py-4">{error || 'Word not found'}</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800 dark:text-white">Word Details</h1>
        <Link
          to="/words"
          className="px-4 py-2 text-sm font-medium text-gray-600 bg-gray-100 rounded-md hover:bg-gray-200 dark:text-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600"
        >
          Back to Words
        </Link>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        <div className="p-6 space-y-4">
          <div>
            <h2 className="text-lg font-semibold text-gray-800 dark:text-white">Japanese</h2>
            <p className="mt-1 text-3xl text-gray-600 dark:text-gray-300">{word.kanji}</p>
          </div>

          <div>
            <h2 className="text-lg font-semibold text-gray-800 dark:text-white">Romaji</h2>
            <p className="mt-1 text-xl text-gray-600 dark:text-gray-300">{word.romaji}</p>
          </div>

          <div>
            <h2 className="text-lg font-semibold text-gray-800 dark:text-white">English</h2>
            <p className="mt-1 text-xl text-gray-600 dark:text-gray-300">{word.english}</p>
          </div>

          <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-800 dark:text-white">Study Statistics</h2>
            <div className="mt-2 grid grid-cols-2 gap-4">
              <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <p className="text-sm text-gray-500 dark:text-gray-400">Correct Answers</p>
                <p className="mt-1 text-2xl font-semibold text-green-500">{word.correct_count}</p>
              </div>
              <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <p className="text-sm text-gray-500 dark:text-gray-400">Wrong Answers</p>
                <p className="mt-1 text-2xl font-semibold text-red-500">{word.wrong_count}</p>
              </div>
            </div>
          </div>

          {word.groups && word.groups.length > 0 && (
            <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
              <h2 className="text-lg font-semibold text-gray-800 dark:text-white">Word Groups</h2>
              <div className="mt-2 flex flex-wrap gap-2">
                {word.groups.map(group => (
                  <Link
                    key={group.id}
                    to={`/groups/${group.id}`}
                    className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-700 hover:bg-blue-200 dark:bg-blue-900 dark:text-blue-100 dark:hover:bg-blue-800"
                  >
                    {group.name}
                  </Link>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}