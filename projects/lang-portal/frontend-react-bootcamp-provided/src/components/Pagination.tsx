import React from 'react'

interface PaginationProps {
  currentPage: number
  totalPages: number
  onPageChange: (page: number) => void
}

export default function Pagination({ currentPage, totalPages, onPageChange }: PaginationProps) {
  if (totalPages <= 1) return null

  return (
    <div className="mt-4 flex justify-center space-x-2">
      <button
        onClick={() => onPageChange(Math.max(1, currentPage - 1))}
        disabled={currentPage === 1}
        className="px-3 py-1 text-sm bg-gray-100 rounded-md disabled:opacity-50 dark:bg-gray-700"
      >
        Previous
      </button>
      <span className="px-3 py-1 text-sm">
        Page {currentPage} of {totalPages}
      </span>
      <button
        onClick={() => onPageChange(Math.min(totalPages, currentPage + 1))}
        disabled={currentPage === totalPages}
        className="px-3 py-1 text-sm bg-gray-100 rounded-md disabled:opacity-50 dark:bg-gray-700"
      >
        Next
      </button>
    </div>
  )
}
