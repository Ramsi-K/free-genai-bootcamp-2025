import React from 'react'
import { Link } from 'react-router-dom'
import { ChevronUp, ChevronDown } from 'lucide-react'
import { StudySession } from '../services/api'

export type StudySessionSortKey = 'id' | 'activity_name' | 'group_name' | 'start_time' | 'end_time' | 'review_items_count'

interface StudySessionsTableProps {
  sessions: StudySession[]
  sortKey: StudySessionSortKey
  sortDirection: 'asc' | 'desc'
  onSort: (key: StudySessionSortKey) => void
}

export default function StudySessionsTable({ 
  sessions, 
  sortKey, 
  sortDirection, 
  onSort 
}: StudySessionsTableProps) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead className="bg-gray-50 dark:bg-gray-900">
          <tr>
            {(['id', 'activity_name', 'group_name', 'start_time', 'end_time', 'review_items_count'] as const).map((key) => (
              <th
                key={key}
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800"
                onClick={() => onSort(key)}
              >
                <div className="flex items-center">
                  {key === 'review_items_count' ? '# Review Items' : key.replace(/_([a-z])/g, ' $1').trim()}
                  {sortKey === key && (
                    sortDirection === 'asc' ? <ChevronUp className="ml-1 h-4 w-4" /> : <ChevronDown className="ml-1 h-4 w-4" />
                  )}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
          {sessions.map((session) => (
            <tr key={session.id} className="bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700">
              <td className="px-6 py-4 whitespace-nowrap">
                <Link to={`/sessions/${session.id}`} className="text-blue-600 dark:text-blue-400 hover:underline">
                  {session.id}
                </Link>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <Link to={`/study-activities/${session.activity_id}`} className="text-blue-600 dark:text-blue-400 hover:underline">
                  {session.activity_name}
                </Link>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <Link to={`/groups/${session.group_id}`} className="text-blue-600 dark:text-blue-400 hover:underline">
                  {session.group_name}
                </Link>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-gray-600 dark:text-gray-300">{session.start_time}</td>
              <td className="px-6 py-4 whitespace-nowrap text-gray-600 dark:text-gray-300">{session.end_time}</td>
              <td className="px-6 py-4 whitespace-nowrap text-gray-600 dark:text-gray-300">{session.review_items_count}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
