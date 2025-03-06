import React from 'react';
import { MessageSquare, Check, X } from 'lucide-react';

type Sentence = {
  id: number;
  korean: string;
  english: string;
  hint: string;
};

const sampleSentences: Sentence[] = [
  {
    id: 1,
    korean: '저는 한국어를 공부해요',
    english: 'I study Korean',
    hint: 'Use formal polite form (-어/아요)',
  },
  {
    id: 2,
    korean: '내일 친구를 만날 거예요',
    english: 'I will meet my friend tomorrow',
    hint: 'Use future tense (-ㄹ/을 거예요)',
  },
];

export default function SentencePractice() {
  const [currentSentenceIndex, setCurrentSentenceIndex] = React.useState(0);
  const [userInput, setUserInput] = React.useState('');
  const [showResult, setShowResult] = React.useState(false);
  const [attempts, setAttempts] = React.useState(0);
  const [correctAttempts, setCorrectAttempts] = React.useState(0);

  const currentSentence = sampleSentences[currentSentenceIndex];

  const handleCheck = () => {
    setShowResult(true);
    setAttempts(prev => prev + 1);
    if (userInput.toLowerCase().trim() === currentSentence.english.toLowerCase()) {
      setCorrectAttempts(prev => prev + 1);
    }
  };

  const handleNext = () => {
    setCurrentSentenceIndex(prev => (prev + 1) % sampleSentences.length);
    setUserInput('');
    setShowResult(false);
  };

  return (
    <div className="space-y-8">
      <div className="glassmorphism rounded-lg p-6">
        <div className="flex items-center space-x-4">
          <MessageSquare className="h-8 w-8 text-yellow-500" />
          <h1 className="text-3xl font-bold">Sentence Practice</h1>
        </div>
        <p className="mt-2 text-foreground/60">
          Accuracy: {attempts > 0 ? Math.round((correctAttempts / attempts) * 100) : 0}%
        </p>
      </div>

      <div className="glassmorphism rounded-lg p-8">
        <div className="space-y-6">
          <div className="text-center">
            <h2 className="text-3xl font-bold mb-2">{currentSentence.korean}</h2>
            <p className="text-foreground/60">{currentSentence.hint}</p>
          </div>

          <div className="space-y-4">
            <textarea
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              placeholder="Type your translation here..."
              className="w-full h-32 p-4 rounded-lg bg-accent/50 focus:bg-accent/70 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all"
              disabled={showResult}
            />

            {!showResult ? (
              <button
                onClick={handleCheck}
                className="w-full py-3 rounded-lg bg-accent hover:bg-accent/80 hover-glow transition-all"
              >
                Check Answer
              </button>
            ) : (
              <div className="space-y-4">
                <div className={`p-4 rounded-lg ${
                  userInput.toLowerCase().trim() === currentSentence.english.toLowerCase()
                    ? 'bg-green-500/20 text-green-500'
                    : 'bg-red-500/20 text-red-500'
                }`}>
                  <div className="flex items-center space-x-2 mb-2">
                    {userInput.toLowerCase().trim() === currentSentence.english.toLowerCase() ? (
                      <Check className="h-5 w-5" />
                    ) : (
                      <X className="h-5 w-5" />
                    )}
                    <span className="font-semibold">
                      {userInput.toLowerCase().trim() === currentSentence.english.toLowerCase()
                        ? 'Correct!'
                        : 'Not quite right'}
                    </span>
                  </div>
                  <p>Correct translation: {currentSentence.english}</p>
                </div>

                <button
                  onClick={handleNext}
                  className="w-full py-3 rounded-lg bg-accent hover:bg-accent/80 hover-glow transition-all"
                >
                  Next Sentence
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}