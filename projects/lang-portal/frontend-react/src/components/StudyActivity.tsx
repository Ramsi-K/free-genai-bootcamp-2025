import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'

type ActivityProps = {
  activity: {
    id: number
    preview_url: string
    title: string
    launch_url: string
  }
}

export default function StudyActivity({ activity }: ActivityProps) {
  return (
    <div className="bg-sidebar rounded-lg shadow-md overflow-hidden">
      <img src={activity.preview_url} alt={activity.title} className="w-full h-48 object-cover" />
      <div className="p-4">
        <h3 className="text-xl font-semibold mb-2">{activity.title}</h3>
        <div className="flex justify-between">
          <Button asChild>
            <Link to={`/study-activities/${activity.id}/launch`}>
              Launch
            </Link>
          </Button>
          <Button asChild variant="outline">
            <Link to={`/study-activities/${activity.id}`}>
              View
            </Link>
          </Button>
        </div>
      </div>
    </div>
  )
}