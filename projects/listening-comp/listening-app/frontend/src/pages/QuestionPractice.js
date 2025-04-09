import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { Container, Box, Button, Alert } from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import LoadingSpinner from '../components/LoadingSpinner';
import PracticeSession from '../components/PracticeSession';
import { useAppContext } from '../context/AppContext';

const QuestionPractice = () => {
  const { videoId } = useParams();
  const { state } = useAppContext();
  const { loading, error } = state;

  if (loading) return <LoadingSpinner message="문제를 불러오는 중..." />;
  if (error) return (
    <Container>
      <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>
      <Button 
        component={Link} 
        to={`/video/${videoId}`}
        startIcon={<ArrowBackIcon />}
        sx={{ mt: 2 }}
      >
        비디오로 돌아가기
      </Button>
    </Container>
  );

  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4 }}>
        <Button
          component={Link}
          to={`/video/${videoId}`}
          startIcon={<ArrowBackIcon />}
          sx={{ mb: 3 }}
        >
          비디오로 돌아가기
        </Button>
        
        <PracticeSession videoId={videoId} />
      </Box>
    </Container>
  );
};

export default QuestionPractice;