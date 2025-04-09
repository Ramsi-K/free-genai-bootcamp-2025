import React from 'react';
import { useParams } from 'react-router-dom';
import QuestionPractice from './QuestionPractice';
import { Box, Container } from '@mui/material';
import { AppProvider } from '../context/AppContext';

const Practice = () => {
  const { videoId } = useParams();

  return (
    <AppProvider>
      <Box sx={{ minHeight: '100vh', backgroundColor: 'background.default' }}>
        <QuestionPractice videoId={videoId} />
      </Box>
    </AppProvider>
  );
};

export default Practice;