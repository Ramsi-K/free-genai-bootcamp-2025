import React, { useState, useEffect } from 'react';
import { 
  Book, 
  CheckCircle, 
  XCircle, 
  Search, 
  Plus, 
  Save, 
  Layers, 
  Hash, 
  ArrowLeft,
  Brain,
  BookOpen,
  Volume2,
  SlidersHorizontal,
  Clock,
  Star,
  Check,
  Headphones,
  Flag
} from 'lucide-react';
import { Link } from 'react-router-dom';
import HagXwonLogo from '../components/HagXwonLogo';

type Word = {
  id: number;
  korean: string;
  romanization: string;
  english: string;
  example: string;
  topikLevel?: number;
  frequency?: number;
  saved?: boolean;
};

type PracticeMode = 'topik' | 'common' | null;
type TopikLevel = 1 | 2 | 3 | 4 | 5 | 6 | null;

// Sample words data
const sampleWords: Word[] = [
  {
    id: 1,
    korean: '안녕하세요',
    romanization: 'annyeonghaseyo',
    english: 'Hello (formal)',
    example: '안녕하세요, 저는 민수입니다.',
    topikLevel: 1,
    frequency: 1,
  },
  {
    id: 2,
    korean: '감사합니다',
    romanization: 'gamsahamnida',
    english: 'Thank you (formal)',
    example: '도와주셔서 감사합니다.',
    topikLevel: 1,
    frequency: 2,
  },
  {
    id: 3,
    korean: '미안합니다',
    romanization: 'mianhamnida',
    english: 'I\'m sorry (formal)',
    example: '늦어서 미안합니다.',
    topikLevel: 1,
    frequency: 3,
  },
  {
    id: 4,
    korean: '이해합니다',
    romanization: 'ihaehabnida',
    english: 'I understand',
    example: '당신의 상황을 이해합니다.',
    topikLevel: 2,
    frequency: 25,
  },
  {
    id: 5,
    korean: '축하합니다',
    romanization: 'chukhahabnida',
    english: 'Congratulations',
    example: '생일 축하합니다!',
    topikLevel: 2,
    frequency: 35,
  },
  {
    id: 6,
    korean: '반갑습니다',
    romanization: 'bangapseumnida',
    english: 'Nice to meet you',
    example: '만나서 반갑습니다.',
    topikLevel: 1,
    frequency: 10,
  },
  {
    id: 7,
    korean: '괜찮아요',
    romanization: 'gwaenchanayo',
    english: 'It\'s okay',
    example: '괜찮아요, 걱정하지 마세요.',
    topikLevel: 1,
    frequency: 5,
  },
  {
    id: 8,
    korean: '잘 부탁드립니다',
    romanization: 'jal butakdeurimnida',
    english: 'Please take care of me / I look forward to working with you',
    example: '앞으로 잘 부탁드립니다.',
    topikLevel: 2,
    frequency: 15,
  },
  {
    id: 9,
    korean: '잘 지냈어요?',
    romanization: 'jal jinaesseoyo',
    english: 'Have you been well?',
    example: '오랜만이에요. 잘 지냈어요?',
    topikLevel: 2,
    frequency: 20,
  },
  {
    id: 10,
    korean: '행복하세요',
    romanization: 'haengbokhaseyo',
    english: 'Be happy',
    example: '항상 행복하세요!',
    topikLevel: 3,
    frequency: 40,
  },
  {
    id: 11,
    korean: '환영합니다',
    romanization: 'hwanyeonghamnida',
    english: 'Welcome',
    example: '우리 회사에 환영합니다.',
    topikLevel: 2,
    frequency: 18,
  },
  {
    id: 12,
    korean: '배고파요',
    romanization: 'baegopayo',
    english: 'I\'m hungry',
    example: '저는 배고파요. 뭐 먹을까요?',
    topikLevel: 1,
    frequency: 8,
  },
];

// Available TOPIK levels
const topikLevels = [1, 2, 3, 4, 5, 6];

// Modal component for settings
type SettingsModalProps = {
  isOpen: boolean;
  onClose: () => void;
  settings: {
    showRomanization: boolean;
    flashcardMode: boolean;
    autoPlayAudio: boolean;
  };
  setSettings: React.Dispatch<React.SetStateAction<{
    showRomanization: boolean;
    flashcardMode: boolean;
    autoPlayAudio: boolean;
  }>>;
};

const SettingsModal: React.FC<SettingsModalProps> = ({ 
  isOpen, 
  onClose, 
  settings, 
  setSettings 
}) => {
  if (!isOpen) return null;
  
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
      <div className="cyber-panel w-full max-w-md animate-float">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold neon-text">Practice Settings</h2>
          <button 
            onClick={onClose}
            className="p-2 rounded-full hover:bg-accent/30 transition-colors"
            aria-label="Close settings"
          >
            <XCircle className="h-5 w-5" />
          </button>
        </div>
        
        <div className="space-y-4">
          <div className="flex justify-between items-center p-3 rounded-lg bg-accent/20">
            <div className="flex items-center">
              <Book className="h-5 w-5 mr-3 text-blue-500" />
              <span>Show Romanization</span>
            </div>
            <div 
              className={`toggle-futuristic ${settings.showRomanization ? 'active' : ''}`}
              onClick={() => setSettings(prev => ({ ...prev, showRomanization: !prev.showRomanization }))}
            ></div>
          </div>
          
          <div className="flex justify-between items-center p-3 rounded-lg bg-accent/20">
            <div className="flex items-center">
              <Layers className="h-5 w-5 mr-3 text-purple-500" />
              <span>Flashcard Mode</span>
            </div>
            <div 
              className={`toggle-futuristic ${settings.flashcardMode ? 'active' : ''}`}
              onClick={() => setSettings(prev => ({ ...prev, flashcardMode: !prev.flashcardMode }))}
            ></div>
          </div>
          
          <div className="flex justify-between items-center p-3 rounded-lg bg-accent/20">
            <div className="flex items-center">
              <Headphones className="h-5 w-5 mr-3 text-green-500" />
              <span>Auto-play Audio</span>
            </div>
            <div 
              className={`toggle-futuristic ${settings.autoPlayAudio ? 'active' : ''}`}
              onClick={() => setSettings(prev => ({ ...prev, autoPlayAudio: !prev.autoPlayAudio }))}
            ></div>
          </div>
        </div>
        
        <button
          onClick={onClose}
          className="w-full mt-6 p-3 btn-futuristic-glow"
        >
          Save Settings
        </button>
      </div>
    </div>
  );
};

// Main Word Practice Component
const WordPractice: React.FC = () => {
  // Main practice state
  const [practiceMode, setPracticeMode] = useState<PracticeMode>(null);
  const [selectedLevel, setSelectedLevel] = useState<TopikLevel>(null);
  const [currentWordIndex, setCurrentWordIndex] = useState(0);
  const [filteredWords, setFilteredWords] = useState<Word[]>([]);
  
  // Word display state
  const [showMeaning, setShowMeaning] = useState(false);
  const [correctCount, setCorrectCount] = useState(0);
  const [incorrectCount, setIncorrectCount] = useState(0);
  
  // Search and results state
  const [showSearchResults, setShowSearchResults] = useState(false);
  const [semanticResults, setSemanticResults] = useState<Word[]>([]);
  const [moreResults, setMoreResults] = useState<Word[]>([]);
  const [savedWords, setSavedWords] = useState<Word[]>([]);
  const [searchLoading, setSearchLoading] = useState(false);

  // Settings and advanced options
  const [showSettings, setShowSettings] = useState(false);
  const [settings, setSettings] = useState({
    showRomanization: true,
    flashcardMode: false,
    autoPlayAudio: false
  });

  // Current word depends on whether we have filtered words or are using the sample
  const currentWord = filteredWords.length > 0 
    ? filteredWords[currentWordIndex % filteredWords.length] 
    : sampleWords[currentWordIndex % sampleWords.length];

  // Time tracking
  const [sessionStartTime, setSessionStartTime] = useState<Date | null>(null);
  const [elapsedTime, setElapsedTime] = useState(0);

  // Initialize session timer
  useEffect(() => {
    if (practiceMode && !sessionStartTime) {
      setSessionStartTime(new Date());
    }

    if (practiceMode && sessionStartTime) {
      const timer = setInterval(() => {
        const now = new Date();
        const elapsed = Math.floor((now.getTime() - sessionStartTime.getTime()) / 1000);
        setElapsedTime(elapsed);
      }, 1000);

      return () => clearInterval(timer);
    }
  }, [practiceMode, sessionStartTime]);

  // Auto-play pronunciation if enabled
  useEffect(() => {
    if (settings.autoPlayAudio && currentWord && !showSearchResults) {
      handlePronounce(currentWord);
    }
  }, [currentWord, settings.autoPlayAudio, showSearchResults]);

  // Preload next word
  useEffect(() => {
    const nextIndex = (currentWordIndex + 1) % filteredWords.length;
    const nextWord = filteredWords[nextIndex];
    if (nextWord) {
      const audio = new Audio();
      audio.src = `path/to/pronunciations/${nextWord.id}.mp3`; // Adjust path as needed
      audio.preload = 'auto';
    }
  }, [currentWordIndex, filteredWords]);
  
  // Persist session state
  useEffect(() => {
    const sessionState = {
      practiceMode,
      selectedLevel,
      currentWordIndex,
      correctCount,
      incorrectCount,
      elapsedTime,
    };
    sessionStorage.setItem('word-practice-state', JSON.stringify(sessionState));
  }, [practiceMode, selectedLevel, currentWordIndex, correctCount, incorrectCount, elapsedTime]);

  // Format time display
  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds < 10 ? '0' : ''}${remainingSeconds}`;
  };

  const handleNext = (isCorrect: boolean) => {
    if (isCorrect) {
      setCorrectCount(prev => prev + 1);
    } else {
      setIncorrectCount(prev => prev + 1);
    }
    
    // Record to study history (placeholder)
    const historyEntry = {
      word: currentWord,
      isCorrect,
      timestamp: new Date().toISOString(),
    };
    console.log('Adding to study history:', historyEntry);
    
    setShowMeaning(false);
    setShowSearchResults(false);
    
    const wordSet = filteredWords.length > 0 ? filteredWords : sampleWords;
    setCurrentWordIndex(prev => (prev + 1) % wordSet.length);
  };

  const handleTopikLevelSelect = (level: number) => {
    setSelectedLevel(level as TopikLevel);
    const filtered = sampleWords.filter(word => word.topikLevel === level);
    setFilteredWords(filtered);
    setPracticeMode('topik');
    setCurrentWordIndex(0);
    setShowMeaning(false);
    setShowSearchResults(false);
    
    // Reset counters
    setCorrectCount(0);
    setIncorrectCount(0);
    
    // Reset timer
    setSessionStartTime(new Date());
    setElapsedTime(0);
  };

  const handleCommonWordsSelect = () => {
    // Sort by frequency (lowest number = most common)
    const filtered = [...sampleWords].sort((a, b) => 
      (a.frequency || 999) - (b.frequency || 999)
    );
    setFilteredWords(filtered);
    setPracticeMode('common');
    setSelectedLevel(null);
    setCurrentWordIndex(0);
    setShowMeaning(false);
    setShowSearchResults(false);
    
    // Reset counters
    setCorrectCount(0);
    setIncorrectCount(0);
    
    // Reset timer
    setSessionStartTime(new Date());
    setElapsedTime(0);
  };

  const handlePronounce = (word: Word) => {
    // Placeholder for TTS API
    console.log(`Playing pronunciation for: ${word.korean}`);
    
    // Visual feedback for the user
    const audioFeedback = document.getElementById('audio-feedback');
    if (audioFeedback) {
      audioFeedback.classList.add('animate-pulse');
      setTimeout(() => {
        audioFeedback.classList.remove('animate-pulse');
      }, 1000);
    }
  };

  const handleSemanticSearch = () => {
    setSearchLoading(true);
    
    // Placeholder for vectorDB API call
    setTimeout(() => {
      // Simulated API response
      const mockResults = [
        {
          id: 101,
          korean: '안녕',
          romanization: 'annyeong',
          english: 'Hello (casual)',
          example: '안녕, 잘 지냈어?',
          topikLevel: 1,
          frequency: 5,
        },
        {
          id: 102,
          korean: '반갑습니다',
          romanization: 'bangapseumnida',
          english: 'Nice to meet you',
          example: '만나서 반갑습니다.',
          topikLevel: 1,
          frequency: 8,
        },
        {
          id: 103,
          korean: '인사하다',
          romanization: 'insahada',
          english: 'To greet',
          example: '아침에 선생님께 인사했어요.',
          topikLevel: 2,
          frequency: 25,
        }
      ];
      
      setSemanticResults(mockResults);
      setShowSearchResults(true);
      setSearchLoading(false);
    }, 1000);
  };

  const handleSearchMore = () => {
    setSearchLoading(true);
    
    // Placeholder for LLM API call
    setTimeout(() => {
      // Simulated API response
      const mockMoreResults = [
        {
          id: 201,
          korean: '잘 가요',
          romanization: 'jal gayo',
          english: 'Goodbye (when someone is leaving)',
          example: '내일 봐요, 잘 가요!',
          topikLevel: 1,
          frequency: 10,
        },
        {
          id: 202,
          korean: '또 만나요',
          romanization: 'tto mannayo',
          english: 'See you again',
          example: '내일 또 만나요!',
          topikLevel: 1,
          frequency: 15,
        },
        {
          id: 203,
          korean: '안녕히 계세요',
          romanization: 'annyeonghi gyeseyo',
          english: 'Goodbye (when you are leaving)',
          example: '저는 이제 가요. 안녕히 계세요.',
          topikLevel: 1,
          frequency: 12,
        },
        {
          id: 204,
          korean: '안녕히 가세요',
          romanization: 'annyeonghi gaseyo',
          english: 'Goodbye (when someone else is leaving)',
          example: '안녕히 가세요, 내일 봐요.',
          topikLevel: 1,
          frequency: 14,
        }
      ];
      
      setMoreResults(mockMoreResults);
      setShowSearchResults(true);
      setSearchLoading(false);
    }, 1500);
  };

  const handleSaveWord = (word: Word) => {
    setSavedWords(prev => [...prev, word]);
    
    // Update semantic or more results to show saved state
    if (semanticResults.some(w => w.id === word.id)) {
      setSemanticResults(prev => 
        prev.map(w => w.id === word.id ? { ...w, saved: true } : w)
      );
    }
    
    if (moreResults.some(w => w.id === word.id)) {
      setMoreResults(prev => 
        prev.map(w => w.id === word.id ? { ...w, saved: true } : w)
      );
    }
    
    // Show confirmation message
    const confirmationElement = document.createElement('div');
    confirmationElement.classList.add('fixed', 'top-4', 'right-4', 'p-4', 'bg-green-500/20', 'text-green-400', 'rounded-lg', 'z-50', 'flex', 'items-center', 'space-x-2');
    confirmationElement.innerHTML = `
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M20 6L9 17l-5-5"></path>
      </svg>
      <span>Word saved successfully!</span>
    `;
    document.body.appendChild(confirmationElement);
    
    setTimeout(() => {
      document.body.removeChild(confirmationElement);
    }, 3000);
  };

  // Reset practice settings
  const handleResetPractice = () => {
    setPracticeMode(null);
    setSelectedLevel(null);
    setCurrentWordIndex(0);
    setShowMeaning(false);
    setShowSearchResults(false);
    setCorrectCount(0);
    setIncorrectCount(0);
    setSessionStartTime(null);
    setElapsedTime(0);
  };

  // If no practice mode is selected, show the selection screen
  if (!practiceMode) {
    return (
      <div className="space-y-8 pt-20">
        <div className="glassmorphism rounded-lg p-6">
          <div className="flex items-center space-x-4 mb-6">
            <Book className="h-8 w-8 text-blue-500" />
            <h1 className="text-3xl font-bold neon-text">Word Practice</h1>
          </div>
          <p className="text-foreground/80 mb-4">Choose a practice mode to begin your Korean vocabulary journey</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="cyber-panel hover-glow transition-transform duration-300 transform hover:scale-105">
            <div className="flex items-center space-x-4 mb-6">
              <Layers className="h-8 w-8 text-blue-500" />
              <h2 className="text-2xl font-bold">Practice by TOPIK Level</h2>
            </div>
            <p className="mb-6 text-foreground/60">Focus on vocabulary for a specific TOPIK exam level</p>
            
            <div className="grid grid-cols-3 gap-4">
              {topikLevels.map(level => (
                <button
                  key={level}
                  onClick={() => handleTopikLevelSelect(level)}
                  className="p-4 rounded-lg bg-accent/30 hover:bg-accent/60 hover-glow flex items-center justify-center transition-all"
                >
                  <div className="relative">
                    <span className="text-lg font-bold">Level {level}</span>
                    <div className="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-blue-500 animate-pulse"></div>
                  </div>
                </button>
              ))}
            </div>
          </div>

          <div className="cyber-panel hover-glow transition-transform duration-300 transform hover:scale-105">
            <div className="flex items-center space-x-4 mb-6">
              <Hash className="h-8 w-8 text-purple-500" />
              <h2 className="text-2xl font-bold">Most Common Words</h2>
            </div>
            <p className="mb-6 text-foreground/60">Learn the most frequently used Korean words first</p>
            
            <button
              onClick={handleCommonWordsSelect}
              className="w-full p-4 rounded-lg bg-accent/30 hover:bg-accent/60 hover-glow transition-all"
            >
              <div className="flex items-center justify-center space-x-2">
                <Star className="h-5 w-5 text-yellow-500" />
                <span>Start Practice</span>
              </div>
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 pt-20">
      {/* Settings modal */}
      <SettingsModal 
        isOpen={showSettings} 
        onClose={() => setShowSettings(false)} 
        settings={settings}
        setSettings={setSettings}
      />
      
      {/* Header with controls */}
      <div className="cyber-panel">
        <div className="flex flex-wrap items-center justify-between">
          <div className="flex items-center space-x-4 mb-4 md:mb-0">
            <Book className="h-8 w-8 text-blue-500" />
            <div>
              <h1 className="text-3xl font-bold neon-text">Word Practice</h1>
              <p className="text-foreground/60">
                {practiceMode === 'topik' 
                  ? `TOPIK Level ${selectedLevel}` 
                  : 'Most Common Words'}
              </p>
            </div>
          </div>
          
          <div className="flex flex-wrap gap-2">
            <button 
              onClick={handleResetPractice}
              className="px-4 py-2 rounded-lg bg-accent/50 hover:bg-accent/70 transition-all flex items-center space-x-2"
            >
              <ArrowLeft className="h-4 w-4" />
              <span>Change Mode</span>
            </button>
            
            <button 
              onClick={() => setShowSettings(true)}
              className="px-4 py-2 rounded-lg bg-accent/50 hover:bg-accent/70 transition-all flex items-center space-x-2"
            >
              <SlidersHorizontal className="h-4 w-4" />
              <span>Settings</span>
            </button>
            
            <Link 
              to="/study-history" 
              className="px-4 py-2 rounded-lg bg-accent/50 hover:bg-accent/70 transition-all flex items-center space-x-2"
            >
              <Clock className="h-4 w-4" />
              <span>History</span>
            </Link>
          </div>
        </div>
        
        <div className="flex flex-wrap justify-between items-center mt-4 pt-4 border-t border-white/10">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-green-500" />
              <span>{correctCount} correct</span>
            </div>
            <div className="flex items-center space-x-2">
              <XCircle className="h-5 w-5 text-red-500" />
              <span>{incorrectCount} incorrect</span>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <Clock className="h-5 w-5 text-blue-500" />
            <span className="font-mono">{formatTime(elapsedTime)}</span>
          </div>
        </div>
      </div>

      {!showSearchResults ? (
        <div className="cyber-panel hover-glow">
          <div className="text-center space-y-6">
            {/* Korean word with pronunciation button */}
            <div className="relative inline-block">
              <h2 className="text-5xl font-bold mb-2 scanner">{currentWord.korean}</h2>
              <button 
                id="audio-feedback"
                className="absolute -right-10 top-1/2 transform -translate-y-1/2 p-2 rounded-full bg-accent/30 hover:bg-accent/50 transition-colors"
                title="Pronounce this word"
                onClick={() => handlePronounce(currentWord)}
              >
                <Volume2 className="h-5 w-5 text-blue-500" />
              </button>
            </div>
            
            {settings.showRomanization && (
              <p className="text-xl text-foreground/60">{currentWord.romanization}</p>
            )}
            
            {settings.flashcardMode && !showMeaning ? (
              <div className="border-2 border-dashed border-white/20 rounded-lg p-8 max-w-md mx-auto">
                <p className="text-foreground/40 italic">Tap to reveal meaning</p>
              </div>
            ) : null}
            
            {showMeaning ? (
              <div className="space-y-4 max-w-2xl mx-auto">
                <div className="p-6 rounded-lg bg-accent/20 neon-border">
                  <p className="text-2xl">{currentWord.english}</p>
                  <p className="text-foreground/60 italic mt-2">"{currentWord.example}"</p>
                </div>
                
                <div className="flex flex-wrap justify-center gap-4 mt-8">
                  <button
                    onClick={() => handleSemanticSearch()}
                    className="px-6 py-3 rounded-lg bg-blue-500/20 text-blue-400 hover:bg-blue-500/30 hover-glow transition-all flex items-center space-x-2"
                    disabled={searchLoading}
                  >
                    {searchLoading ? (
                      <div className="animate-spin h-5 w-5 border-2 border-blue-500 border-t-transparent rounded-full"></div>
                    ) : (
                      <Search className="h-5 w-5" />
                    )}
                    <span>Semantic Search</span>
                  </button>
                  
                  <button
                    onClick={() => handleSearchMore()}
                    className="px-6 py-3 rounded-lg bg-purple-500/20 text-purple-400 hover:bg-purple-500/30 hover-glow transition-all flex items-center space-x-2"
                    disabled={searchLoading}
                  >
                    {searchLoading ? (
                      <div className="animate-spin h-5 w-5 border-2 border-purple-500 border-t-transparent rounded-full"></div>
                    ) : (
                      <Plus className="h-5 w-5" />
                    )}
                    <span>Search More</span>
                  </button>
                </div>
                
                <div className="flex justify-center space-x-4 mt-4">
                  <button
                    onClick={() => handleNext(true)}
                    className="px-6 py-3 rounded-lg bg-green-500/20 text-green-400 hover:bg-green-500/30 hover-glow transition-all flex items-center space-x-2"
                  >
                    <Check className="h-5 w-5" />
                    <span>I knew this</span>
                  </button>
                  <button
                    onClick={() => handleNext(false)}
                    className="px-6 py-3 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30 hover-glow transition-all flex items-center space-x-2"
                  >
                    <Flag className="h-5 w-5" />
                    <span>Need to review</span>
                  </button>
                </div>
              </div>
            ) : (
              <button
                onClick={() => setShowMeaning(true)}
                className="px-6 py-3 rounded-lg btn-futuristic-glow"
              >
                Show Meaning
              </button>
            )}
          </div>
        </div>
      ) : (
        <div className="cyber-panel">
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold neon-text">Related Words</h2>
              <button
                onClick={() => setShowSearchResults(false)}
                className="px-4 py-2 rounded-lg bg-accent/50 hover:bg-accent/70 transition-all flex items-center space-x-2"
              >
                <ArrowLeft className="h-5 w-5" />
                <span>Back to Practice</span>
              </button>
            </div>
            
            {semanticResults.length > 0 && (
              <div>
                <h3 className="text-xl font-semibold mb-4 flex items-center">
                  <Brain className="h-5 w-5 mr-2 text-blue-500" />
                  <span>Semantic Results</span>
                </h3>
                <div className="space-y-4">
                  {semanticResults.map(word => (
                    <div key={word.id} className="glassmorphism p-5 rounded-lg hover-glow">
                      <div className="flex justify-between items-start">
                        <div>
                          <div className="flex items-center space-x-3">
                            <p className="text-lg font-bold">{word.korean}</p>
                            <button 
                              className="p-1 rounded-full bg-accent/30 hover:bg-accent/50 transition-colors"
                              title="Pronounce this word"
                              onClick={() => handlePronounce(word)}
                            >
                              <Volume2 className="h-4 w-4 text-blue-500" />
                            </button>
                          </div>
                          <p className="text-sm text-foreground/60">{word.romanization}</p>
                          <p className="mt-1">{word.english}</p>
                          <p className="text-sm italic text-foreground/60 mt-1">{word.example}</p>
                        </div>
                        <button
                          onClick={() => handleSaveWord(word)}
                          className={`p-2 rounded-lg ${
                            word.saved 
                              ? 'bg-green-500/30 text-green-400' 
                              : 'bg-blue-500/20 text-blue-400 hover:bg-blue-500/30'
                          } hover-glow transition-all`}
                          disabled={word.saved}
                        >
                          {word.saved ? (
                            <CheckCircle className="h-5 w-5" />
                          ) : (
                            <Save className="h-5 w-5" />
                          )}
                        </button>
                      </div>
                    </div>
                  ))}