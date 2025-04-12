import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useThemeStore } from './store/theme';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import WordPractice from './pages/WordPractice';
import ListeningPractice from './pages/ListeningPractice';
import SentencePractice from './pages/SentencePractice';
import StudyHistoryPage from './pages/StudyHistoryPage';
import AdminPage from './pages/AdminPage';

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
              <Route path="/word-practice" element={<WordPractice />} />
              <Route path="/listening-practice" element={<ListeningPractice />} />
              <Route path="/sentence-practice" element={<SentencePractice />} />
              <Route path="/study-history" element={<StudyHistoryPage />} />
              <Route path="/admin" element={<AdminPage />} />
            </Routes>
          </main>
        </div>
      </Router>
    </div>
  );
}

export default App;