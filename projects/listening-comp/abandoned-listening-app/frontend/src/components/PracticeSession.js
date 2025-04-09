import React, { useEffect, useState } from 'react';
import { 
  Box, Typography, LinearProgress, Card, Button, 
  Fade 
} from '@mui/material';
import AudioPlayer from './AudioPlayer';
import { useAppContext } from '../context/AppContext';
import { questionAPI } from '../services/api';
import { withRetry } from '../utils/retryUtil';
import SessionManager from '../services/sessionManager';

const PracticeSession = ({ videoId }) => {
  const { state, actions } = useAppContext();
  const { session } = state;
  const [feedback, setFeedback] = useState(null);

  useEffect(() => {
    const savedSession = SessionManager.loadSession();
    if (savedSession?.videoId === videoId) {
      actions.startPractice(
        savedSession.videoId,
        savedSession.difficulty,
        savedSession.questions,
        savedSession.currentQuestionIndex,
        savedSession.answers,
        savedSession.score
      );
      actions.showInfo('이전 세션을 복구했습니다.');
    } else {
      loadQuestions();
    }
  }, [videoId]);

  useEffect(() => {
    if (session.videoId) {
      SessionManager.saveSession(session);
    }
  }, [session]);

  const loadQuestions = async () => {
    try {
      actions.startLoading();
      const response = await withRetry(() => questionAPI.getByVideo(videoId));
      if (response.data.success) {
        actions.startPractice(
          videoId,
          response.data.level,
          response.data.questions
        );
      }
    } catch (err) {
      actions.showError('문제를 불러오는데 실패했습니다.');
    } finally {
      actions.stopLoading();
    }
  };

  const handleAnswerSubmit = async (answer, isCorrect) => {
    actions.submitAnswer(answer, isCorrect);
    actions.showNotification(
      isCorrect ? '정답입니다!' : '틀렸습니다. 다시 들어보세요.',
      isCorrect ? 'success' : 'error',
      1500
    );

    try {
      await questionAPI.submitAnswer(videoId, 
        session.currentQuestionIndex, 
        { answer, isCorrect }
      );
    } catch (err) {
      console.error('Failed to save answer:', err);
    }

    if (session.currentQuestionIndex + 1 >= session.questions.length) {
      const score = session.score + (isCorrect ? 1 : 0);
      const total = session.questions.length;
      const percentage = (score / total) * 100;

      setTimeout(() => {
        actions.showNotification(
          `연습이 끝났습니다! 점수: ${score}/${total} (${percentage.toFixed(1)}%)`,
          percentage >= 70 ? 'success' : 'info',
          5000
        );
      }, 2000);
    }
  };

  const handleReset = () => {
    SessionManager.clearSession();
    actions.resetSession();
    actions.showInfo('새로운 연습을 시작합니다.');
    loadQuestions();
  };

  const currentQuestion = session.questions[session.currentQuestionIndex];

  return (
    <Box>
      <LinearProgress 
        variant="determinate" 
        value={(session.currentQuestionIndex / session.questions.length) * 100} 
      />
      
      <Fade in={Boolean(currentQuestion)} timeout={500}>
        <Card sx={{ mt: 2, p: 2 }}>
          {currentQuestion && (
            <>
              <Typography variant="h6" gutterBottom>
                문제 {session.currentQuestionIndex + 1} / {session.questions.length}
              </Typography>
              
              <AudioPlayer 
                src={questionAPI.getAudio(currentQuestion.audio_url)}
                onEnded={() => actions.setAudioPlaying(false)}
              />
              
              <Box sx={{ mt: 2 }}>
                {currentQuestion.options.map((option, idx) => (
                  <Button
                    key={idx}
                    fullWidth
                    variant="outlined"
                    sx={{ 
                      mt: 1,
                      backgroundColor: feedback && idx === currentQuestion.correct ? 
                        'success.lighter' : undefined
                    }}
                    onClick={() => handleAnswerSubmit(idx, idx === currentQuestion.correct)}
                    disabled={session.audioPlaying || feedback}
                  >
                    {option}
                  </Button>
                ))}
              </Box>
            </>
          )}
        </Card>
      </Fade>

      {session.completed && (
        <Fade in timeout={1000}>
          <Box sx={{ mt: 2, textAlign: 'center' }}>
            <Typography variant="h5" gutterBottom>
              연습 완료!
            </Typography>
            <Typography variant="h6" color={session.score > session.questions.length / 2 ? 'success.main' : 'error.main'}>
              점수: {session.score} / {session.questions.length}
            </Typography>
            <Button
              variant="contained"
              onClick={handleReset}
              sx={{ mt: 2 }}
            >
              다시 시작하기
            </Button>
          </Box>
        </Fade>
      )}
    </Box>
  );
};

export default PracticeSession;