import { useEffect, useState } from 'react'
import StudyActivity from '@/components/StudyActivity'

type ActivityCard = {
  id: number
  preview_url: string
  title: string
  launch_url: string
}

export default function StudyActivities() {
  const [activities, setActivities] = useState<ActivityCard[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch('http://localhost:5000/api/study-activities')
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to fetch study activities')
        }
        return response.json()
      })
      .then(data => {
        setActivities(data)
        setLoading(false)
      })
      .catch(err => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return <div className="text-center">Loading study activities...</div>
  }

  if (error) {
    return <div className="text-red-500">Error: {error}</div>
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {activities.map((activity) => (
        <StudyActivity key={activity.id} activity={activity} />
      ))}
    </div>
  )
}