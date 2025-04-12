import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../../lib/api';
import type { DashboardStats, StudyProgress, StudyActivity } from '../../types/api';

const DEFAULT_ACTIVITIES = [
  {
    id: 1,
    name: "Flashcards",
    url: "/flashcards",
    thumbnail_url: "/images/flashcards.png",
  },
  {
    id: 2,
    name: "Listening",
    url: "/listening-practice",
    thumbnail_url: "/images/listening.png",
  },
  {
    id: 3,
    name: "Writing",
    url: "/writing",
    thumbnail_url: "/images/writing.png",
  },
  {
    id: 4,
    name: "Word Muncher",
    url: "/games/muncher",
    thumbnail_url: "/images/muncher.png",
  }
];

const Dashboard = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [progress, setProgress] = useState<StudyProgress | null>(null);
  const [activities, setActivities] = useState<StudyActivity[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        const [statsData, progressData, activitiesData] = await Promise.all([
          api.getDashboardStats(),
          api.getStudyProgress(),
          api.getStudyActivities(),
        ]);
        setStats(statsData);
        setProgress(progressData);
        setActivities(activitiesData.length ? activitiesData : DEFAULT_ACTIVITIES);
      } catch (error) {
        console.error('Failed to load dashboard data:', error);
        setActivities(DEFAULT_ACTIVITIES); // Fallback to default activities
      }
    };
    loadDashboard();
  }, []);

  return (
    <div className="space-y-8">
      <section className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Quick Stats */}
        <div className="hud-element">
          <h2 className="text-xl font-bold mb-4 neon-text">Quick Stats</h2>
          {stats && (
            <div className="space-y-2">
              <p>Total Words: {stats.total_words}</p>
              <p>Total Groups: {stats.total_groups}</p>
              <p>Study Sessions: {stats.total_sessions}</p>
            </div>
          )}
        </div>

        {/* Study Progress */}
        <div className="hud-element">
          <h2 className="text-xl font-bold mb-4 neon-text">Progress</h2>
          {progress && (
            <div className="space-y-2">
              <p>Correct: {progress.correct}</p>
              <p>Incorrect: {progress.incorrect}</p>
              <div className="progress-bar" />
            </div>
          )}
        </div>

        {/* Quick Actions */}
        <div className="hud-element">
          <h2 className="text-xl font-bold mb-4 neon-text">Quick Actions</h2>
          <div className="flex flex-col space-y-2">
            <Link to="/word-practice" className="btn-futuristic">
              Start Learning
            </Link>
            <Link to="/games/muncher" className="btn-futuristic">
              Play Word Muncher
            </Link>
          </div>
        </div>
      </section>

      {/* Study Activities Grid */}
      <section className="grid-pattern p-8 rounded-lg glassmorphism">
        <h2 className="text-2xl font-bold mb-6 neon-text">Study Activities</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {(activities.length ? activities : DEFAULT_ACTIVITIES).map((activity) => (
            <div
              key={activity.id}
              onClick={() => navigate(activity.url)}
              className="hud-element hover-glow cursor-pointer transform transition-transform hover:scale-105"
            >
              <div className="flex flex-col items-center text-center">
                {activity.thumbnail_url && (
                  <img 
                    src={activity.thumbnail_url} 
                    alt={activity.name}
                    className="w-16 h-16 mb-2 opacity-70"
                  />
                )}
                <h3 className="text-lg font-bold neon-text">{activity.name}</h3>
                <p className="text-sm opacity-70">Practice your skills</p>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default Dashboard;
