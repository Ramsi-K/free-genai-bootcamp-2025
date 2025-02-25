import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { BookOpen, Trophy, Clock, ArrowRight, Activity } from 'lucide-react'
import { fetchRecentStudySession, fetchStudyStats, type StudyStats, type RecentSession } from '@/services/api'

interface DashboardCardProps {
  title: string
  icon: React.ElementType
  children: React.ReactNode
  className?: string
}

function DashboardCard({ title, icon: Icon, children, className = '' }: DashboardCardProps) {
  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 ${className}`}>
      <div className="flex items-center gap-2 mb-4">
        <Icon className="w-5 h-5 text-blue-500" />
        <h2 className="text-lg font-semibold">{title}</h2>
      </div>
      {children}
    </div>
  )
}

export default function Dashboard() {
  const [recentSession, setRecentSession] = useState<RecentSession | null>(null)
  const [stats, setStats] = useState<StudyStats | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        const [sessionData, statsData] = await Promise.all([
          fetchRecentStudySession(),
          fetchStudyStats()
        ])
        setRecentSession(sessionData)
        setStats(statsData)
      } catch (error) {
        console.error('Failed to load dashboard data:', error)
      } finally {
        setIsLoading(false)
      }
    }

    loadDashboardData()
  }, [])

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <Link 
          to="/study-activities"
          className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          Start Studying
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Last Study Session */}
        <DashboardCard title="Last Study Session" icon={Clock}>
          {isLoading ? (
            <div className="animate-pulse h-20 bg-gray-200 dark:bg-gray-700 rounded" />
          ) : recentSession ? (
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-300">{recentSession.activity_name}</span>
                <span className="text-sm text-gray-500">{new Date(recentSession.created_at).toLocaleDateString()}</span>
              </div>
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-1">
                  <span className="text-green-500">✓</span>
                  <span>{recentSession.correct_count} correct</span>
                </div>
                <div className="flex items-center gap-1">
                  <span className="text-red-500">✗</span>
                  <span>{recentSession.wrong_count} wrong</span>
                </div>
              </div>
              <Link 
                to={`/groups/${recentSession.group_id}`}
                className="inline-flex items-center gap-1 text-sm text-blue-500 hover:text-blue-600"
              >
                View Group <ArrowRight className="w-3 h-3" />
              </Link>
            </div>
          ) : (
            <div className="text-center py-6">
              <p className="text-gray-500 mb-4">No sessions yet</p>
              <Link 
                to="/study-activities"
                className="text-blue-500 hover:text-blue-600 inline-flex items-center gap-1"
              >
                Start your first session <ArrowRight className="w-3 h-3" />
              </Link>
            </div>
          )}
        </DashboardCard>

        {/* Study Progress */}
        <DashboardCard title="Study Progress" icon={Activity}>
          {isLoading ? (
            <div className="animate-pulse space-y-4">
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4" />
              <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded" />
            </div>
          ) : stats ? (
            <div className="space-y-4">
              {stats.total_words_studied > 0 ? (
                <>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-300">Total Words Studied</span>
                    <span className="text-2xl font-semibold">{stats.total_words_studied} / {stats.total_vocabulary}</span>
                  </div>
                  <div className="relative pt-1">
                    <div className="flex mb-2 items-center justify-between">
                      <div>
                        <span className="text-xs font-semibold inline-block text-blue-600">
                          Mastery Progress
                        </span>
                      </div>
                      <div className="text-right">
                        <span className="text-xs font-semibold inline-block text-blue-600">
                          {Math.round((stats.mastered_words / stats.total_vocabulary) * 100)}%
                        </span>
                      </div>
                    </div>
                    <div className="overflow-hidden h-2 text-xs flex rounded bg-blue-200">
                      <div
                        style={{ width: `${(stats.mastered_words / stats.total_vocabulary) * 100}%` }}
                        className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-blue-500"
                      />
                    </div>
                  </div>
                </>
              ) : (
                <div className="text-center py-6">
                  <p className="text-gray-500 mb-4">Start studying to see your progress</p>
                  <Link 
                    to="/groups"
                    className="text-blue-500 hover:text-blue-600 inline-flex items-center gap-1"
                  >
                    Browse word groups <ArrowRight className="w-3 h-3" />
                  </Link>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-6">
              <p className="text-gray-500 mb-4">Start studying to see your progress</p>
              <Link 
                to="/groups"
                className="text-blue-500 hover:text-blue-600 inline-flex items-center gap-1"
              >
                Browse word groups <ArrowRight className="w-3 h-3" />
              </Link>
            </div>
          )}
        </DashboardCard>

        {/* Quick Stats */}
        <DashboardCard title="Quick Stats" icon={Trophy}>
          {isLoading ? (
            <div className="animate-pulse space-y-3">
              {[1, 2, 3].map(i => (
                <div key={i} className="h-4 bg-gray-200 dark:bg-gray-700 rounded" />
              ))}
            </div>
          ) : stats ? (
            <div className="space-y-3">
              {stats.total_sessions > 0 ? (
                <>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-300">Success Rate</span>
                    <span className="font-medium">{Math.round(stats.success_rate * 100)}%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-300">Study Sessions</span>
                    <span className="font-medium">{stats.total_sessions}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-300">Active Groups</span>
                    <span className="font-medium">{stats.active_groups}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-300">Study Streak</span>
                    <span className="font-medium">{stats.current_streak} days</span>
                  </div>
                </>
              ) : (
                <div className="text-center py-6">
                  <p className="text-gray-500 mb-4">Complete sessions to see your stats</p>
                  <Link 
                    to="/study-activities"
                    className="text-blue-500 hover:text-blue-600 inline-flex items-center gap-1"
                  >
                    Try an activity <ArrowRight className="w-3 h-3" />
                  </Link>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-6">
              <p className="text-gray-500 mb-4">Complete sessions to see your stats</p>
              <Link 
                to="/study-activities"
                className="text-blue-500 hover:text-blue-600 inline-flex items-center gap-1"
              >
                Try an activity <ArrowRight className="w-3 h-3" />
              </Link>
            </div>
          )}
        </DashboardCard>
      </div>
    </div>
  )
}