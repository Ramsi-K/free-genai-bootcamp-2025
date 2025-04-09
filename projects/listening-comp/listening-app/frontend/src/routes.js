import React, { Suspense, lazy } from 'react';
import { Routes, Route } from 'react-router-dom';
import LoadingSpinner from './components/LoadingSpinner';

// Lazy load components for better performance
const HomePage = lazy(() => import('./pages/HomePage'));
const VideoList = lazy(() => import('./pages/VideoList'));
const VideoDetail = lazy(() => import('./pages/VideoDetail'));
const QuestionPractice = lazy(() => import('./pages/QuestionPractice'));
const NotFound = lazy(() => import('./pages/NotFound'));

const AppRoutes = () => {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/videos" element={<VideoList />} />
        <Route path="/video/:videoId" element={<VideoDetail />} />
        <Route path="/practice/:videoId" element={<QuestionPractice />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Suspense>
  );
};

export default AppRoutes;