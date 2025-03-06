import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Activity, Book, Headphones, MessageSquare, BrainCircuit, Zap, Trophy, TrendingUp } from 'lucide-react';
import HagXwonLogo from './HagXwonLogo';

// Animated waveform component for listening section
const AudioWaveform = () => {
  const [bars, setBars] = useState<number[]>([]);
  
  useEffect(() => {
    // Generate random bars for visualization
    const generateBars = () => {
      const newBars = Array.from({ length: 20 }, () => Math.random() * 100);
      setBars(newBars);
    };
    
    // Update bars every 500ms for animation effect
    const interval = setInterval(generateBars, 500);
    generateBars(); // Initial generation
    
    return () => clearInterval(interval);
  }, []);
  
  return (
    <div className="flex items-end justify-between h-12 px-2">
      {bars.map((height, index) => (
        <div 
          key={index}
          style={{ height: `${height}%` }}
          className="w-1 bg-gradient-to-t from-blue-500 to-purple-500 rounded-t-lg"
        />
      ))}
    </div>
  );
};

// Circular progress indicator
const CircularProgress = ({ value, max, label, color }: { value: number, max: number, label: string, color: string }) => {
  const percentage = (value / max) * 100;
  const circumference = 2 * Math.PI * 40; // radius = 40
  const offset = circumference - (percentage / 100) * circumference;
  
  return (
    <div className="flex flex-col items-center">
      <div className="relative h-24 w-24">
        <svg className="w-full h-full" viewBox="0 0 100 100">
          {/* Background circle */}
          <circle
            cx="50"
            cy="50"
            r="40"
            fill="transparent"
            stroke="rgba(255, 255, 255, 0.1)"
            strokeWidth="8"
          />
          {/* Progress circle */}
          <circle
            cx="50"
            cy="50"
            r="40"
            fill="transparent"
            stroke={color}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            transform="rotate(-90 50 50)"
            className="animate-pulse-glow"
          />
          {/* Text value */}
          <text
            x="50"
            y="50"
            fontFamily="sans-serif"
            fontSize="18"
            textAnchor="middle"
            dominantBaseline="middle"
            fill="white"
          >
            {value}
          </text>
        </svg>
      </div>
      <span className="mt-2 text-sm text-foreground/60">{label}</span>
    </div>
  );
};

// Holographic card component
const HolographicCard = ({ children, className }: { children: React.ReactNode, className?: string }) => {
  return (
    <div className={`glassmorphism rounded-lg p-6 border border-white/10 animate-glow relative ${className}`}>
      <div className="absolute inset-0 rounded-lg overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-500/5 opacity-30"></div>
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-blue-500/50 to-transparent"></div>
        <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-purple-500/50 to-transparent"></div>
      </div>
      <div className="relative">{children}</div>
    </div>
  );
};

export default function Dashboard() {
  const [currentUser, setCurrentUser] = useState({
    name: 'Language Learner',
    level: 'Intermediate',
    streak: 12,
    points: 2450,
    progress: 75,
  });

  // Simulate data loading
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const timer = setTimeout(() => {
      setLoading(false);
    }, 1000);
    
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="space-y-8 pt-20">
      {/* Hero section */}
      <HolographicCard>
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <div>
            <h1 className="text-4xl font-bold mb-2 neon-text">Welcome back, {currentUser.name}!</h1>
            <p className="text-foreground/80 mb-4">Continue your Korean language journey</p>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Zap className="h-5 w-5 text-yellow-400" />
                <span className="font-medium">{currentUser.streak} day streak</span>
              </div>
              <div className="flex items-center space-x-2">
                <Trophy className="h-5 w-5 text-yellow-400" />
                <span className="font-medium">{currentUser.points} points</span>
              </div>
            </div>
            
            <div className="mt-6">
              <button className="btn-futuristic py-3 px-8 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 text-white hover-glow transition-all flex items-center space-x-2">
                <BrainCircuit className="h-5 w-5" />
                <span>Continue Learning</span>
              </button>
            </div>
          </div>
          
          <div className="relative flex-shrink-0">
            <div className="relative h-48 w-48">
              <div className="absolute inset-0 rounded-full bg-gradient-to-br from-blue-500/20 to-purple-500/20 blur-lg animate-pulse"></div>
              <div className="absolute h-48 w-48 rounded-full bg-black/80 backdrop-blur-sm border border-white/10 flex items-center justify-center">
                <HagXwonLogo variant="gradient" size="xl" />
              </div>
              <div className="absolute top-0 left-0 right-0 bottom-0 rotate-45">
                <div className="h-full w-full border-2 border-white/5 rounded-full"></div>
              </div>
              <div className="absolute top-0 left-0 right-0 bottom-0 -rotate-45">
                <div className="h-full w-full border-2 border-white/5 rounded-full"></div>
              </div>
            </div>
          </div>
        </div>
      </HolographicCard>

      {/* Stats grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <HolographicCard className="hover-glow transition-transform duration-300 transform hover:scale-105">
          <div className="flex items-center space-x-4">
            <Activity className="h-8 w-8 text-blue-500" />
            <div>
              <h3 className="font-semibold">Study Progress</h3>
              <div className="w-full bg-black/30 rounded-full h-2 mt-2">
                <div 
                  className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full animate-pulse-glow"
                  style={{ width: `${currentUser.progress}%` }}
                ></div>
              </div>
              <p className="text-sm text-foreground/60 mt-1">{currentUser.progress}% Complete</p>
            </div>
          </div>
        </HolographicCard>

        <HolographicCard className="hover-glow transition-transform duration-300 transform hover:scale-105">
          <div className="flex items-center space-x-4">
            <Book className="h-8 w-8 text-purple-500" />
            <div>
              <h3 className="font-semibold">Words Learned</h3>
              <p className="text-2xl font-bold">247</p>
              <p className="text-sm text-foreground/60">
                <span className="text-green-400">+12</span> this week
              </p>
            </div>
          </div>
        </HolographicCard>

        <HolographicCard className="hover-glow transition-transform duration-300 transform hover:scale-105">
          <div className="flex items-center space-x-4">
            <Headphones className="h-8 w-8 text-green-500" />
            <div>
              <h3 className="font-semibold">Listening Score</h3>
              <p className="text-2xl font-bold">92%</p>
              <div className="mt-1">
                <AudioWaveform />
              </div>
            </div>
          </div>
        </HolographicCard>

        <HolographicCard className="hover-glow transition-transform duration-300 transform hover:scale-105">
          <div className="flex items-center space-x-4">
            <MessageSquare className="h-8 w-8 text-yellow-500" />
            <div>
              <h3 className="font-semibold">Speaking Practice</h3>
              <p className="text-2xl font-bold">15</p>
              <p className="text-sm text-foreground/60">Practice sessions</p>
            </div>
          </div>
        </HolographicCard>
      </div>

      {/* Progress charts and recommendations */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <HolographicCard>
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <TrendingUp className="h-5 w-5 mr-2 text-blue-500" />
            Progress Breakdown
          </h2>
          <div className="flex justify-around">
            <CircularProgress value={85} max={100} label="Words" color="#4A90E2" />
            <CircularProgress value={72} max={100} label="Listening" color="#6B2FB3" />
            <CircularProgress value={64} max={100} label="Sentences" color="#FFA500" />
          </div>
        </HolographicCard>

        <HolographicCard>
          <h2 className="text-xl font-semibold mb-4">Recommended Next</h2>
          <div className="space-y-4">
            <Link 
              to="/word-practice"
              className="block w-full text-left p-4 rounded-md bg-accent/30 hover:bg-accent/50 hover-glow transition-all border border-white/5"
            >
              <div className="flex items-center">
                <div className="p-2 rounded-full bg-blue-500/20 mr-3">
                  <Book className="h-5 w-5 text-blue-500" />
                </div>
                <div>
                  <h3 className="font-semibold">TOPIK Level 2 - Lesson 5</h3>
                  <p className="text-sm text-foreground/60">Continue where you left off</p>
                </div>
              </div>
            </Link>
            
            <Link
              to="/listening-practice"
              className="block w-full text-left p-4 rounded-md bg-accent/30 hover:bg-accent/50 hover-glow transition-all border border-white/5"
            >
              <div className="flex items-center">
                <div className="p-2 rounded-full bg-purple-500/20 mr-3">
                  <Headphones className="h-5 w-5 text-purple-500" />
                </div>
                <div>
                  <h3 className="font-semibold">Practice Common Phrases</h3>
                  <p className="text-sm text-foreground/60">15 new expressions</p>
                </div>
              </div>
            </Link>
          </div>
        </HolographicCard>
      </div>

      {/* Recent activity */}
      <HolographicCard>
        <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-3 rounded-lg bg-accent/20 border border-white/5">
            <div className="flex items-center">
              <div className="p-2 rounded-full bg-blue-500/20 mr-3">
                <Book className="h-4 w-4 text-blue-500" />
              </div>
              <span>Completed Word Practice</span>
            </div>
            <span className="text-sm text-foreground/60">2h ago</span>
          </div>
          
          <div className="flex items-center justify-between p-3 rounded-lg bg-accent/20 border border-white/5">
            <div className="flex items-center">
              <div className="p-2 rounded-full bg-purple-500/20 mr-3">
                <Headphones className="h-4 w-4 text-purple-500" />
              </div>
              <span>Listening Exercise</span>
            </div>
            <span className="text-sm text-foreground/60">5h ago</span>
          </div>
          
          <div className="flex items-center justify-between p-3 rounded-lg bg-accent/20 border border-white/5">
            <div className="flex items-center">
              <div className="p-2 rounded-full bg-yellow-500/20 mr-3">
                <MessageSquare className="h-4 w-4 text-yellow-500" />
              </div>
              <span>Grammar Quiz</span>
            </div>
            <span className="text-sm text-foreground/60">1d ago</span>
          </div>
          
          <Link
            to="/study-history"
            className="block text-center py-2 text-sm text-blue-400 hover:text-blue-300 transition-colors"
          >
            View Full History
          </Link>
        </div>
      </HolographicCard>
    </div>
  );
}