import { useState } from 'react'
import { useTheme } from '@/components/theme-provider'

export default function Settings() {
  const { theme, setTheme } = useTheme()
  const [showResetDialog, setShowResetDialog] = useState(false)
  const [resetConfirmation, setResetConfirmation] = useState('')

  const handleReset = async () => {
    if (resetConfirmation.toLowerCase() === 'reset me') {
      try {
        const response = await fetch('http://localhost:5000/api/study-sessions/reset', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error('Failed to reset history');
        }

        // Reset was successful
        setShowResetDialog(false);
        setResetConfirmation('');
        
        // Show success message
        alert('Study history has been cleared successfully');
      } catch (error) {
        console.error('Error resetting history:', error);
        alert('Failed to reset history. Please try again.');
      }
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800 dark:text-white">Settings</h1>
      
      <div className="flex items-center justify-between">
        <span className="text-gray-700 dark:text-gray-300">Theme</span>
        <select
          value={theme}
          onChange={(e) => setTheme(e.target.value as 'light' | 'dark' | 'system')}
          className="bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md px-3 py-1 text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="light">Light</option>
          <option value="dark">Dark</option>
          <option value="system">System</option>
        </select>
      </div>

      <div>
        <button
          onClick={() => setShowResetDialog(true)}
          className="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded"
        >
          Reset History
        </button>
      </div>

      {showResetDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg">
            <h2 className="text-xl font-bold mb-4 text-gray-800 dark:text-white">Confirm Reset</h2>
            <p className="mb-4 text-gray-600 dark:text-gray-400">
              Type "reset me" to confirm database reset:
            </p>
            <input
              type="text"
              value={resetConfirmation}
              onChange={(e) => setResetConfirmation(e.target.value)}
              className="border rounded px-2 py-1 mb-4 w-full text-gray-800 dark:text-white dark:bg-gray-700"
            />
            <div className="flex justify-end space-x-2">
              <button
                onClick={() => setShowResetDialog(false)}
                className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded"
              >
                Cancel
              </button>
              <button
                onClick={handleReset}
                className="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded"
              >
                Confirm Reset
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}