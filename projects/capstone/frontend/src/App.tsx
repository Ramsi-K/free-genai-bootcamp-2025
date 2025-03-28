import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useThemeStore } from './store/theme';
import Navbar from './components/layout/Navbar';
import Dashboard from './components/layout/Dashboard';
import KoreanMuncher from './components/games/Munchers/KoreanMuncher';
import FlashcardActivity from './components/activities/FlashcardActivity';

// Still using placeholders for these routes
const WordPractice = () => <div>Word Practice</div>;
const ListeningPractice = () => <div>Listening Practice</div>;
const SentencePractice = () => <div>Sentence Practice</div>;
const StudyHistoryPage = () => <div>Study History</div>;
const AdminPage = () => <div>Admin</div>;

function App() {
  const theme = useThemeStore((state) => state.theme);

  return (
    <div className={theme}>
      <Router>
        <div className="min-h-screen bg-background text-foreground">
          <Navbar />
          <main className="container mx-auto px-4 py-8">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/flashcards" element={<FlashcardActivity />} />
              <Route path="/word-practice" element={<WordPractice />} />
              <Route path="/listening-practice" element={<ListeningPractice />} />
              <Route path="/sentence-practice" element={<SentencePractice />} />
              <Route path="/study-history" element={<StudyHistoryPage />} />
              <Route path="/admin" element={<AdminPage />} />
              <Route path="/games/muncher" element={<KoreanMuncher />} />
              <Route path="/games/muncher/:groupId" element={<KoreanMuncher />} />
            </Routes>
          </main>
        </div>
      </Router>
    </div>
  );
}

export default App;