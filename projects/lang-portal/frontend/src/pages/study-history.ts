import React, { useState } from 'react';
import { History, Filter, Calendar, Clock, Book, Headphones, MessageSquare, Award, ChevronDown, ChevronUp } from 'lucide-react';

type ActivityType = 'word' | 'listening' | 'sentence' | 'grammar' | 'all';
type ActivityRecord = {
  id: number;
  type: 'word' | 'listening' | 'sentence' | 'grammar';
  detail: string;
  timestamp: string;
  score?: number;
  duration?: number;
  completed: boolean;
};

// Sample activity data
const sampleActivities: ActivityRecord[] = [
  {
    id: 1,
    type: 'word',
    detail: 'TOPIK Level 1 Words',
    timestamp: '2025-03-06T09:30:00',
    score: 85,
    duration: 15,
    completed: true
  },
  {
    id: 2,
    type: 'listening',
    detail: 'Basic Conversations',
    timestamp: '2025-03-05T14:45:00',
    score: 70,
    duration: 20,
    completed: true
  },
  {
    id: 3,
    type: 'sentence',
    detail: 'Present Tense Practice',
    timestamp: '2025-03-05T11:20:00',
    score: 90,
    duration: 18,
    completed: true
  },
  {
    id: 4,
    type: 'grammar',
    detail: 'Particles Usage',
    timestamp: '2025-03-04T16:10:00',
    score: 65,
    duration: 25,
    completed: true
  },
  {
    id: 5,
    type: 'word',
    detail: 'Common Words',
    timestamp: '2025-03-04T10:00:00',
    score: 95,
    duration: 12,
    completed: true
  },
  {
    id: 6,
    type: 'listening',
    detail: 'TOPIK Practice Questions',
    timestamp: '2025-03-03T15:30:00',
    score: 80,
    duration: 30,
    completed: true
  },
  {
    id: 7,
    type: 'sentence',
    detail: 'Past Tense Formation',
    timestamp: '2025-03-02T18:45:00',
    score: 75,
    duration: 22,
    completed: true
  },
  {
    id: 8,
    type: 'word',
    detail: 'TOPIK Level 2 Words',
    timestamp: '2025-03-01T11:15:00',
    duration: 10,
    completed: false
  }
];

const StudyHistory = () => {
  const [activeFilter, setActiveFilter] = useState<ActivityType>('all');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [expandedActivity, setExpandedActivity] = useState<number | null>(null);

  // Filter activities based on selected type
  const filteredActivities = activeFilter === 'all'
    ? sampleActivities
    : sampleActivities.filter(activity => activity.type === activeFilter);

  // Sort activities by timestamp
  const sortedActivities = [...filteredActivities].sort((a, b) => {
    const dateA = new Date(a.timestamp).getTime();
    const dateB = new Date(b.timestamp).getTime();
    return sortOrder === 'desc' ? dateB - dateA : dateA - dateB;
  });

  // Helper function to format timestamp
  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      year: 'numeric'
    });
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit'
    });
  };

  // Get activity icon based on type
  const getActivityIcon = (type: string) => {
    switch(type) {
      case 'word':
        return <Book className="h-5 w-5 text-blue-500" />;
      case 'listening':
        return <Headphones className="h-5 w-5 text-purple-500" />;
      case 'sentence':
        return <MessageSquare className="h-5 w-5 text-yellow-500" />;
      case 'grammar':
        return <Award className="h-5 w-5 text-green-500" />;
      default:
        return <Book className="h-5 w-5" />;
    }
  };

  // Get score color based on value
  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-500';
    if (score >= 70) return 'text-yellow-500';
    return 'text-red-500';
  };

  return (
    <div className="space-y-8">
      <div className="glassmorphism rounded-lg p-6">
        <div className="flex items-center space-x-4">
          <History className="h-8 w-8 text-blue-500" />
          <h1 className="text-3xl font-bold">Study History</h1>
        </div>
        <p className="mt-2 text-foreground/60">Track your learning progress over time</p>
      </div>

      <div className="glassmorphism rounded-lg p-6">
        <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
          <div className="flex items-center space-x-2">
            <Filter className="h-5 w-5 text-blue-500" />
            <span className="font-semibold">Filter:</span>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setActiveFilter('all')}
              className={`px-4 py-2 rounded-lg transition-all ${
                activeFilter === 'all' 
                  ? 'bg-accent text-foreground' 
                  : 'bg-accent/30 text-foreground/60 hover:bg-accent/50'
              }`}
            >
              All
            </button>
            <button
              onClick={() => setActiveFilter('word')}
              className={`px-4 py-2 rounded-lg transition-all flex items-center space-x-2 ${
                activeFilter === 'word' 
                  ? 'bg-accent text-foreground' 
                  : 'bg-accent/30 text-foreground/60 hover:bg-accent/50'
              }`}
            >
              <Book className="h-4 w-4" />
              <span>Words</span>
            </button>
            <button
              onClick={() => setActiveFilter('listening')}
              className={`px-4 py-2 rounded-lg transition-all flex items-center space-x-2 ${
                activeFilter === 'listening' 
                  ? 'bg-accent text-foreground' 
                  : 'bg-accent/30 text-foreground/60 hover:bg-accent/50'
              }`}
            >
              <Headphones className="h-4 w-4" />
              <span>Listening</span>
            </button>
            <button
              onClick={() => setActiveFilter('sentence')}
              className={`px-4 py-2 rounded-lg transition-all flex items-center space-x-2 ${
                activeFilter === 'sentence' 
                  ? 'bg-accent text-foreground' 
                  : 'bg-accent/30 text-foreground/60 hover:bg-accent/50'
              }`}
            >
              <MessageSquare className="h-4 w-4" />
              <span>Sentences</span>
            </button>
            <button
              onClick={() => setActiveFilter('grammar')}
              className={`px-4 py-2 rounded-lg transition-all flex items-center space-x-2 ${
                activeFilter === 'grammar' 
                  ? 'bg-accent text-foreground' 
                  : 'bg-accent/30 text-foreground/60 hover:bg-accent/50'
              }`}
            >
              <Award className="h-4 w-4" />
              <span>Grammar</span>
            </button>
          </div>
          <button
            onClick={() => setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc')}
            className="px-4 py-2 rounded-lg bg-accent/30 hover:bg-accent/50 transition-all flex items-center space-x-2"
          >
            <Calendar className="h-4 w-4" />
            <span>Sort: {sortOrder === 'desc' ? 'Newest First' : 'Oldest First'}</span>
            {sortOrder === 'desc' ? (
              <ChevronDown className="h-4 w-4" />
            ) : (
              <ChevronUp className="h-4 w-4" />
            )}
          </button>
        </div>

        <div className="space-y-4">
          {sortedActivities.length > 0 ? (
            sortedActivities.map(activity => (
              <div 
                key={activity.id} 
                className="glassmorphism rounded-lg p-4 hover-glow transition-all cursor-pointer"
                onClick={() => setExpandedActivity(expandedActivity === activity.id ? null : activity.id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    {getActivityIcon(activity.type)}
                    <div>
                      <h3 className="font-semibold">{activity.detail}</h3>
                      <div className="flex items-center space-x-4 text-sm text-foreground/60">
                        <div className="flex items-center space-x-1">
                          <Calendar className="h-3 w-3" />
                          <span>{formatDate(activity.timestamp)}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Clock className="h-3 w-3" />
                          <span>{formatTime(activity.timestamp)}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    {activity.score && (
                      <div className={`font-semibold ${getScoreColor(activity.score)}`}>
                        {activity.score}%
                      </div>
                    )}
                    