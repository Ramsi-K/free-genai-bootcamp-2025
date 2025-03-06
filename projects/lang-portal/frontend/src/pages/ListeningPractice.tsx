import React from 'react';
import { Headphones, Volume2 } from 'lucide-react';

type ListeningQuestion = {
  id: number;
  audioUrl: string;
  korean: string;
  options: string[];
  correctAnswer: number;
};

const sampleQuestions: ListeningQuestion[] = [
  {
    id: 1,
    audioUrl: 'https://example.com/audio1.mp3',
    korean: '오늘 날씨가 좋네요',
    options: [
      'The weather is nice today',
      'I like this restaurant',
      'Nice to meet you',
      'See you tomorrow'
    ],
    correctAnswer: 0
  },
  {
    id: 2,
    audioUrl: 'https://example.com/audio2.mp3',
    korean: '이것 좀 도와주세요',
    options: [
      'Where is the bathroom?',
      'Please help me with this',
      'What time is it?',
      'How much is this?'
    ],
    correctAnswer: 1
  }
];

export default function ListeningPractice() {
  const [currentQuestionIndex, setCurrentQuestionIndex] = React.useState(0);
  const [selectedAnswer, setSelectedAnswer] = React.useState<number | null>(null);
  const [score, setScore] = React.useState(0);

  const currentQuestion = sampleQuestions[currentQuestionIndex];

  const handleAnswer = (optionIndex: number) => {
    setSelectedAnswer(optionIndex);
    if (optionIndex === currentQuestion.correctAnswer) {
      setScore(prev => prev + 1);
    }
  };

  const handleNext = () => {
    setSelectedAnswer(null);
    setCurrentQuestionIndex(prev => (prev + 1) % sampleQuestions.length);
  };

  return (
    <div className="space-y-8">
      <div className="glassmorphism rounded-lg p-6">
        <div className="flex items-center space-x-4">
          <Headphones className="h-8 w-8 text-purple-500" />
          <h1 className="text-3xl font-bold">Listening Practice</h1>
        </div>
        <p className="mt-2 text-foreground/60">Score: {score}/{sampleQuestions.length}</p>
      </div>

      <div className="glassmorphism rounded-lg p-8">
        <div className="text-center space-y-8">
          <button
            className="p-8 rounded-full bg-accent hover:bg-accent/80 hover-glow transition-all"
            onClick={() => {/* Play audio */}}
          >
            <Volume2 className="h-12 w-12" />
          </button>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {currentQuestion.options.map((option, index) => (
              <button
                key={index}
                onClick={() => handleAnswer(index)}
                className={`p-4 rounded-lg text-left transition-all ${
                  selectedAnswer === null
                    ? 'bg-accent hover:bg-accent/80 hover-glow'
                    : selectedAnswer === index
                    ? index === currentQuestion.correctAnswer
                      ? 'bg-green-500/20 text-green-500'
                      : 'bg-red-500/20 text-red-500'
                    : index === currentQuestion.correctAnswer
                    ? 'bg-green-500/20 text-green-500'
                    : 'bg-accent/50'
                }`}
                disabled={selectedAnswer !== null}
              >
                {option}
              </button>
            ))}
          </div>

          {selectedAnswer !== null && (
            <div className="mt-8">
              <p className="text-xl mb-4">{currentQuestion.korean}</p>
              <button
                onClick={handleNext}
                className="px-6 py-3 rounded-lg bg-accent hover:bg-accent/80 hover-glow transition-all"
              >
                Next Question
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}