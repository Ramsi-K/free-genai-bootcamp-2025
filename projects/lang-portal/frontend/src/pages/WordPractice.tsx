import React from 'react';
import { Book, CheckCircle, XCircle } from 'lucide-react';

type Word = {
  id: number;
  korean: string;
  romanization: string;
  english: string;
  example: string;
};

const sampleWords: Word[] = [
  {
    id: 1,
    korean: '안녕하세요',
    romanization: 'annyeonghaseyo',
    english: 'Hello (formal)',
    example: '안녕하세요, 저는 민수입니다.',
  },
  {
    id: 2,
    korean: '감사합니다',
    romanization: 'gamsahamnida',
    english: 'Thank you (formal)',
    example: '도와주셔서 감사합니다.',
  },
  {
    id: 3,
    korean: '미안합니다',
    romanization: 'mianhamnida',
    english: 'I\'m sorry (formal)',
    example: '늦어서 미안합니다.',
  },
];

export default function WordPractice() {
  const [currentWordIndex, setCurrentWordIndex] = React.useState(0);
  const [showMeaning, setShowMeaning] = React.useState(false);
  const [correctCount, setCorrectCount] = React.useState(0);
  const [incorrectCount, setIncorrectCount] = React.useState(0);

  const currentWord = sampleWords[currentWordIndex];

  const handleNext = (isCorrect: boolean) => {
    if (isCorrect) {
      setCorrectCount(prev => prev + 1);
    } else {
      setIncorrectCount(prev => prev + 1);
    }
    
    setShowMeaning(false);
    setCurrentWordIndex(prev => (prev + 1) % sampleWords.length);
  };

  return (
    <div className="space-y-8">
      <div className="glassmorphism rounded-lg p-6">
        <div className="flex items-center space-x-4 mb-6">
          <Book className="h-8 w-8 text-blue-500" />
          <h1 className="text-3xl font-bold">Word Practice</h1>
        </div>
        <div className="flex justify-between mb-4">
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

      <div className="glassmorphism rounded-lg p-8">
        <div className="text-center space-y-6">
          <h2 className="text-4xl font-bold mb-2">{currentWord.korean}</h2>
          <p className="text-xl text-foreground/60">{currentWord.romanization}</p>
          
          {showMeaning ? (
            <div className="space-y-4">
              <p className="text-2xl">{currentWord.english}</p>
              <p className="text-foreground/60 italic">"{currentWord.example}"</p>
              
              <div className="flex justify-center space-x-4 mt-8">
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
    </div>
  );
}