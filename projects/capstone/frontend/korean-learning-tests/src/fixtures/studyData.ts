// src/fixtures/studyData.ts
// Realistic test fixtures for study session history

export const studySessionHistory = [
  {
    id: 'session-1',
    type: 'word',
    startTime: '2023-10-01T10:00:00Z',
    endTime: '2023-10-01T10:30:00Z',
    correctCount: 15,
    incorrectCount: 5,
    wordsPracticed: [
      { word: '안녕하세요', correct: true },
      { word: '감사합니다', correct: true },
      { word: '사랑', correct: false },
      { word: '학교', correct: true },
      { word: '친구', correct: false },
    ],
  },
  {
    id: 'session-2',
    type: 'listening',
    startTime: '2023-10-02T14:00:00Z',
    endTime: '2023-10-02T14:45:00Z',
    correctCount: 10,
    incorrectCount: 2,
    wordsPracticed: [
      { word: '사람', correct: true },
      { word: '물', correct: true },
      { word: '책', correct: false },
      { word: '음악', correct: true },
      { word: '영화', correct: true },
    ],
  },
  {
    id: 'session-3',
    type: 'sentence',
    startTime: '2023-10-03T09:00:00Z',
    endTime: '2023-10-03T09:30:00Z',
    correctCount: 8,
    incorrectCount: 4,
    wordsPracticed: [
      { word: '나는 학생입니다', correct: true },
      { word: '그는 의사입니다', correct: false },
      { word: '우리는 친구입니다', correct: true },
      { word: '그녀는 선생님입니다', correct: true },
      { word: '이것은 책입니다', correct: false },
    ],
  },
];