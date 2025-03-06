import React from 'react';
import { Activity, Book, Headphones, MessageSquare } from 'lucide-react';

export default function Dashboard() {
  return (
    <div className="space-y-8">
      <div className="glassmorphism rounded-lg p-6">
        <h1 className="text-3xl font-bold mb-4">Welcome back!</h1>
        <p className="text-foreground/80">Continue your Korean language journey</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="glassmorphism rounded-lg p-6 hover-glow">
          <div className="flex items-center space-x-4">
            <Activity className="h-8 w-8 text-blue-500" />
            <div>
              <h3 className="font-semibold">Study Progress</h3>
              <p className="text-sm text-foreground/60">75% Complete</p>
            </div>
          </div>
        </div>

        <div className="glassmorphism rounded-lg p-6 hover-glow">
          <div className="flex items-center space-x-4">
            <Book className="h-8 w-8 text-purple-500" />
            <div>
              <h3 className="font-semibold">Words Learned</h3>
              <p className="text-sm text-foreground/60">247 words</p>
            </div>
          </div>
        </div>

        <div className="glassmorphism rounded-lg p-6 hover-glow">
          <div className="flex items-center space-x-4">
            <Headphones className="h-8 w-8 text-green-500" />
            <div>
              <h3 className="font-semibold">Listening Score</h3>
              <p className="text-sm text-foreground/60">92%</p>
            </div>
          </div>
        </div>

        <div className="glassmorphism rounded-lg p-6 hover-glow">
          <div className="flex items-center space-x-4">
            <MessageSquare className="h-8 w-8 text-yellow-500" />
            <div>
              <h3 className="font-semibold">Speaking Practice</h3>
              <p className="text-sm text-foreground/60">15 sessions</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glassmorphism rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span>Completed Word Practice</span>
              <span className="text-sm text-foreground/60">2h ago</span>
            </div>
            <div className="flex items-center justify-between">
              <span>Listening Exercise</span>
              <span className="text-sm text-foreground/60">5h ago</span>
            </div>
            <div className="flex items-center justify-between">
              <span>Grammar Quiz</span>
              <span className="text-sm text-foreground/60">1d ago</span>
            </div>
          </div>
        </div>

        <div className="glassmorphism rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Recommended Next</h2>
          <div className="space-y-4">
            <button className="w-full text-left p-4 rounded-md bg-accent hover:bg-accent/80 transition-colors">
              <h3 className="font-semibold">TOPIK Level 2 - Lesson 5</h3>
              <p className="text-sm text-foreground/60">Continue where you left off</p>
            </button>
            <button className="w-full text-left p-4 rounded-md bg-accent hover:bg-accent/80 transition-colors">
              <h3 className="font-semibold">Practice Common Phrases</h3>
              <p className="text-sm text-foreground/60">15 new expressions</p>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}