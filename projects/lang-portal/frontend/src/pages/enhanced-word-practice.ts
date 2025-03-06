import React, { useState } from 'react';
import { Book, CheckCircle, XCircle, Search, Plus, Save, Layers, Hash } from 'lucide-react';
import { Link } from 'react-router-dom';

type Word = {
  id: number;
  korean: string;
  romanization: string;
  english: string;
  example: string;
  topikLevel?: number;
  frequency?: number;
};

type PracticeMode = 'topik' | 'common';

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
];

const topikLevels = [1, 2, 3, 4, 5, 6];

export default function WordPractice() {
  const [currentWordIndex, setCurrentWordIndex] = useState(0);
  const [showMeaning, setShowMeaning] = useState(false);
  const [correctCount, setCorrectCount] = useState(0);
  const [incorrectCount, setIncorrectCount] = useState(0);
  
  const [practiceMode, setPracticeMode] = useState<PracticeMode | null>(null);
  const [selectedLevel, setSelectedLevel] = useState<number | null>(null);
  const [filteredWords, setFilteredWords] = useState<Word[]>([]);
  
  const [showSearchResults, setShowSearchResults] = useState(false);
  const [semanticResults, setSemanticResults] = useState<Word[]>([]);
  const [moreResults, setMoreResults] = useState<Word[]>([]);
  const [savedWords, setSavedWords] = useState<Word[]>([]);

  // Current word depends on whether we have filtered words or are using the sample
  const currentWord = filteredWords.length > 0 
    ? filteredWords[currentWordIndex % filteredWords.length] 
    : sampleWords[currentWordIndex % sampleWords.length];

  const handleNext = (isCorrect: boolean) => {
    if (isCorrect) {
      setCorrectCount(prev => prev + 1);
    } else {
      setIncorrectCount(prev => prev + 1);
    }
    
    setShowMeaning(false);
    setShowSearchResults(false);
    
    const wordSet = filteredWords.length > 0 ? filteredWords : sampleWords;
    setCurrentWordIndex(prev => (prev + 1) % wordSet.length);
  };

  const handleTopikLevelSelect = (level: number) => {
    setSelectedLevel(level);
    const filtered = sampleWords.filter(word => word.topikLevel === level);
    setFilteredWords(filtered);
    setPracticeMode('topik');
    setCurrentWordIndex(0);
    setShowMeaning(false);
    setShowSearchResults(false);
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
  };

  const handleSemanticSearch = () => {
    // This would call your vectorDB API in a real implementation
    // Simulating results for now
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
      }
    ];
    
    setSemanticResults(mockResults);
    setShowSearchResults(true);
  };

  const handleSearchMore = () => {
    // This would call your LLM API in a real implementation
    // Simulating results for now
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
      }
    ];
    
    setMoreResults(mockMoreResults);
    setShowSearchResults(true);
  };

  const handleSaveWord = (word: Word) => {
    setSavedWords(prev => [...prev, word]);
    // In a real app, you would also send this to your vectorDB
    alert(`Saved "${word.korean}" to your word collection!`);
  };

  // If no practice mode is selected, show the selection screen
  if (!practiceMode) {
    return (
      <div className="space-y-8">
        <div className="glassmorphism rounded-lg p-6">
          <div className="flex items-center space-x-4 mb-6">
            <Book className="h-8 w-8 text-blue-500" />
            <h1 className="text-3xl font-bold">Word Practice</h1>
          </div>
          <p className="text-foreground/80 mb-4">Choose a practice mode to begin</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="glassmorphism rounded-lg p-8 hover-glow transition-all">
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
                  className="p-4 rounded-lg bg-accent hover:bg-accent/80 hover-glow flex items-center justify-center"
                >
                  Level {level}
                </button>
              ))}
            </div>
          </div>

          <div className="glassmorphism rounded-lg p-8 hover-glow transition-all">
            <div className="flex items-center space-x-4 mb-6">
              <Hash className="h-8 w-8 text-purple-500" />
              <h2 className="text-2xl font-bold">Most Common Words</h2>
            </div>
            <p className="mb-6 text-foreground/60">Learn the most frequently used Korean words first</p>
            
            <button
              onClick={handleCommonWordsSelect}
              className="w-full p-4 rounded-lg bg-accent hover:bg-accent/80 hover-glow"
            >
              Start Practice
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="glassmorphism rounded-lg p-6">
        <div className="flex flex-wrap items-center justify-between">
          <div className="flex items-center space-x-4 mb-4 md:mb-0">
            <Book className="h-8 w-8 text-blue-500" />
            <div>
              <h1 className="text-3xl font-bold">Word Practice</h1>
              <p className="text-foreground/60">
                {practiceMode === 'topik' 
                  ? `TOPIK Level ${selectedLevel}` 
                  : 'Most Common Words'}
              </p>
            </div>
          </div>
          
          <div className="flex space-x-4">
            <button 
              onClick={() => setPracticeMode(null)}
              className="px-4 py-2 rounded-lg bg-accent/50 hover:bg-accent/80 transition-all"
            >
              Change Mode
            </button>
            
            <Link 
              to="/study-history" 
              className="px-4 py-2 rounded-lg bg-accent/50 hover:bg-accent/80 transition-all"
            >
              View History
            </Link>
          </div>
        </div>
        
        <div className="flex justify-between mt-4">
          <div className="flex items-center space-x-2">
            <CheckCircle className="h-5 w-5 text-green-500" />
            <span>{correctCount} correct</span>
          </div>
          <div className="flex items-center space-x-2">
            <XCircle className="h-5 w-5 text-red-500" />
            <span>{incorrectCount} incorrect</span>
          </div>
        </div>
      </div>

      {!showSearchResults ? (
        <div className="glassmorphism rounded-lg p-8">
          <div className="text-center space-y-6">
            <h2 className="text-4xl font-bold mb-2">{currentWord.korean}</h2>
            <p className="text-xl text-foreground/60">{currentWord.romanization}</p>
            
            {showMeaning ? (
              <div className="space-y-4">
                <p className="text-2xl">{currentWord.english}</p>
                <p className="text-foreground/60 italic">"{currentWord.example}"</p>
                
                <div className="flex flex-wrap justify-center gap-4 mt-8">
                  <button
                    onClick={() => handleSemanticSearch()}
                    className="px-6 py-3 rounded-lg bg-blue-500/20 text-blue-500 hover:bg-blue-500/30 hover-glow transition-all flex items-center space-x-2"
                  >
                    <Search className="h-5 w-5" />
                    <span>Semantic Search</span>
                  </button>
                  
                  <button
                    onClick={() => handleSearchMore()}
                    className="px-6 py-3 rounded-lg bg-purple-500/20 text-purple-500 hover:bg-purple-500/30 hover-glow transition-all flex items-center space-x-2"
                  >
                    <Plus className="h-5 w-5" />
                    <span>Search More</span>
                  </button>
                </div>
                
                <div className="flex justify-center space-x-4 mt-4">
                  <button
                    onClick={() => handleNext(true)}
                    className="px-6 py-3 rounded-lg bg-green-500/20 text-green-500 hover:bg-green-500/30 hover-glow transition-all"
                  >
                    I knew this
                  </button>
                  <button
                    onClick={() => handleNext(false)}
                    className="px-6 py-3 rounded-lg bg-red-500/20 text-red-500 hover:bg-red-500/30 hover-glow transition-all"
                  >
                    Need to review
                  </button>
                </div>
              </div>
            ) : (
              <button
                onClick={() => setShowMeaning(true)}
                className="px-6 py-3 rounded-lg bg-accent hover:bg-accent/80 hover-glow transition-all"
              >
                Show Meaning
              </button>
            )}
          </div>
        </div>
      ) : (
        <div className="glassmorphism rounded-lg p-8">
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">Related Words</h2>
              <button
                onClick={() => setShowSearchResults(false)}
                className="px-4 py-2 rounded-lg bg-accent/50 hover:bg-accent/80 transition-all"
              >
                Back to Practice
              </button>
            </div>
            
            {semanticResults.length > 0 && (
              <div>
                <h3 className="text-xl font-semibold mb-4">Semantic Results</h3>
                <div className="space-y-4">
                  {semanticResults.map(word => (
                    <div key={word.id} className="glassmorphism p-4 rounded-lg">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="text-lg font-bold">{word.korean}</p>
                          <p className="text-sm text-foreground/60">{word.romanization}</p>
                          <p>{word.english}</p>
                          <p className="text-sm italic text-foreground/60 mt-1">{word.example}</p>
                        </div>
                        <button
                          onClick={() => handleSaveWord(word)}
                          className="p-2 rounded-lg bg-green-500/20 text-green-500 hover:bg-green-500/30 hover-glow transition-all"
                        >
                          <Save className="h-5 w-5" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {moreResults.length > 0 && (
              <div>
                <h3 className="text-xl font-semibold mb-4">More Results</h3>
                <div className="space-y-4">
                  {moreResults.map(word => (
                    <div key={word.id} className="glassmorphism p-4 rounded-lg">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="text-lg font-bold">{word.korean}</p>
                          <p className="text-sm text-foreground/60">{word.romanization}</p>
                          <p>{word.english}</p>
                          <p className="text-sm italic text-foreground/60 mt-1">{word.example}</p>
                        </div>
                        <button
                          onClick={() => handleSaveWord(word)}
                          className="p-2 rounded-lg bg-green-500/20 text-green-500 hover:bg-green-500/30 hover-glow transition-all"
                        >
                          <Save className="h-5 w-5" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
