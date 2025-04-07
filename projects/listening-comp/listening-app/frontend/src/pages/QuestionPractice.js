import React, { useState, useEffect, useRef } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
  Container, 
  Typography, 
  Paper, 
  Box,
  Grid,
  Button,
  Radio,
  RadioGroup,
  FormControlLabel,
  FormControl,
  FormLabel,
  Card,
  CardContent,
  CardActions,
  Stepper,
  Step,
  StepLabel,
  IconButton,
  CircularProgress,
  Alert,
  Snackbar,
  Divider,
  LinearProgress
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';
import NavigateBeforeIcon from '@mui/icons-material/NavigateBefore';
import HomeIcon from '@mui/icons-material/Home';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import VolumeUpIcon from '@mui/icons-material/VolumeUp';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ReplayIcon from '@mui/icons-material/Replay';
import InfoIcon from '@mui/icons-material/Info';

// API endpoint configuration
const AUDIO_API_URL = process.env.REACT_APP_AUDIO_API_URL || 'http://localhost:5002';
const QUESTION_API_URL = process.env.REACT_APP_QUESTION_API_URL || 'http://localhost:5001';

const QuestionPractice = () => {
  const { videoId } = useParams();
  const navigate = useNavigate();
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeStep, setActiveStep] = useState(0);
  const [selectedOption, setSelectedOption] = useState('');
  const [showAnswer, setShowAnswer] = useState(false);
  const [isCorrect, setIsCorrect] = useState(false);
  const [score, setScore] = useState(0);
  const [progress, setProgress] = useState(0);
  const [audioPlaying, setAudioPlaying] = useState(false);
  const audioRef = useRef(null);
  const [videoTitle, setVideoTitle] = useState('');

  useEffect(() => {
    fetchQuestions();
  }, [videoId]);

  useEffect(() => {
    // Update progress when activeStep or questions length changes
    if (questions.length > 0) {
      setProgress(((activeStep + 1) / questions.length) * 100);
    }
  }, [activeStep, questions.length]);

  const fetchQuestions = async () => {
    try {
      const response = await axios.get(`${AUDIO_API_URL}/api/audio-questions/${videoId}`);
      
      if (response.data.success && response.data.questions.length > 0) {
        setQuestions(response.data.questions);
        
        // Attempt to get video title
        try {
          const videoResponse = await axios.get(`${QUESTION_API_URL}/api/questions/${videoId}`);
          if (videoResponse.data.success) {
            setVideoTitle(videoResponse.data.data.metadata?.title || '');
          }
        } catch (err) {
          console.error('Error fetching video details:', err);
        }
      } else {
        setError('이 비디오에 대한 문제가 아직 생성되지 않았습니다.');
      }
    } catch (err) {
      console.error('Error fetching questions:', err);
      setError('문제를 불러오는 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    // If we're showing the answer, go to the next question
    if (showAnswer) {
      setActiveStep((prevActiveStep) => prevActiveStep + 1);
      setSelectedOption('');
      setShowAnswer(false);
      setAudioPlaying(false);
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
      }
    } else {
      // If we're not showing the answer, check the answer
      checkAnswer();
    }
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
    setSelectedOption('');
    setShowAnswer(false);
    setAudioPlaying(false);
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
  };

  const checkAnswer = () => {
    if (!selectedOption) {
      return; // Don't check if no option is selected
    }
    
    const currentQuestion = questions[activeStep];
    const correctAnswer = currentQuestion.correct_answer;
    const correct = selectedOption === correctAnswer;
    
    setIsCorrect(correct);
    setShowAnswer(true);
    
    if (correct) {
      setScore(prevScore => prevScore + 1);
    }
  };

  const handleOptionChange = (event) => {
    setSelectedOption(event.target.value);
  };

  const handlePlayAudio = () => {
    const currentQuestion = questions[activeStep];
    const audioUrl = currentQuestion.audio_url;
    
    if (audioRef.current && audioUrl) {
      if (audioPlaying) {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
        setAudioPlaying(false);
      } else {
        audioRef.current.play();
        setAudioPlaying(true);
      }
    }
  };

  const handleAudioEnded = () => {
    setAudioPlaying(false);
  };

  const restartPractice = () => {
    setActiveStep(0);
    setSelectedOption('');
    setShowAnswer(false);
    setScore(0);
    setProgress(0);
    setAudioPlaying(false);
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
  };

  if (loading) {
    return (
      <Container maxWidth="md">
        <Box display="flex" justifyContent="center" my={4}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="md">
        <Alert severity="error" sx={{ my: 2 }}>{error}</Alert>
        <Button 
          component={Link} 
          to={`/videos/${videoId}`} 
          startIcon={<ArrowBackIcon />}
          sx={{ mr: 2 }}
        >
          비디오 상세 정보로 돌아가기
        </Button>
      </Container>
    );
  }

  if (questions.length === 0) {
    return (
      <Container maxWidth="md">
        <Alert severity="info" sx={{ my: 2 }}>
          이 비디오에 대한 문제가 없습니다. 비디오 상세 페이지에서 문제를 생성해 주세요.
        </Alert>
        <Button 
          component={Link} 
          to={`/videos/${videoId}`} 
          startIcon={<ArrowBackIcon />}
        >
          비디오 상세 정보로 돌아가기
        </Button>
      </Container>
    );
  }

  // If we've finished all the questions
  if (activeStep === questions.length) {
    return (
      <Container maxWidth="md">
        <Paper elevation={3} sx={{ p: 4, my: 4, textAlign: 'center' }}>
          <CheckCircleIcon color="success" sx={{ fontSize: 80, mb: 2 }} />
          <Typography variant="h4" gutterBottom>
            연습 완료!
          </Typography>
          <Typography variant="h5" color="primary" gutterBottom>
            점수: {score} / {questions.length} ({Math.round((score / questions.length) * 100)}%)
          </Typography>
          <Typography variant="body1" paragraph>
            {score === questions.length ? 
              '완벽합니다! 모든 문제를 맞혔습니다.' : 
              '수고하셨습니다! 계속 연습하면 더 좋아질 거예요.'}
          </Typography>
          <Box display="flex" justifyContent="center" mt={3}>
            <Button 
              variant="outlined" 
              startIcon={<HomeIcon />}
              component={Link}
              to="/videos"
              sx={{ mr: 2 }}
            >
              비디오 목록으로
            </Button>
            <Button 
              variant="contained" 
              color="primary"
              startIcon={<ReplayIcon />}
              onClick={restartPractice}
            >
              다시 연습하기
            </Button>
          </Box>
        </Paper>
      </Container>
    );
  }

  const currentQuestion = questions[activeStep];
  const audioUrl = currentQuestion.audio_url;

  return (
    <Container maxWidth="md">
      <Box mb={2} display="flex" alignItems="center">
        <Button 
          component={Link} 
          to={`/videos/${videoId}`} 
          startIcon={<ArrowBackIcon />}
          sx={{ mr: 2 }}
        >
          돌아가기
        </Button>
        <Typography variant="h5" sx={{ flexGrow: 1 }}>
          듣기 연습
        </Typography>
        <Typography variant="body2" color="textSecondary">
          점수: {score} / {activeStep + (showAnswer ? 1 : 0)}
        </Typography>
      </Box>

      {videoTitle && (
        <Typography variant="subtitle1" color="textSecondary" gutterBottom>
          {videoTitle}
        </Typography>
      )}

      <LinearProgress 
        variant="determinate" 
        value={progress} 
        sx={{ mb: 3, height: 8, borderRadius: 4 }} 
        color="primary"
      />

      <Card elevation={3}>
        <CardContent>
          <Box mb={3} display="flex" justifyContent="center">
            <Button
              variant="contained"
              color={audioPlaying ? "secondary" : "primary"}
              startIcon={audioPlaying ? <VolumeUpIcon /> : <PlayArrowIcon />}
              onClick={handlePlayAudio}
              disabled={!audioUrl}
              size="large"
            >
              {audioPlaying ? "듣는 중..." : "문제 듣기"}
            </Button>
            {audioUrl && (
              <audio 
                ref={audioRef}
                src={audioUrl} 
                onEnded={handleAudioEnded}
                style={{ display: 'none' }}
              />
            )}
          </Box>

          <Typography variant="h6" gutterBottom>
            문제 {activeStep + 1}: {currentQuestion.question}
          </Typography>

          <FormControl component="fieldset" sx={{ mt: 2, width: '100%' }}>
            <RadioGroup
              name="question-options"
              value={selectedOption}
              onChange={handleOptionChange}
            >
              {Object.entries(currentQuestion.options).map(([key, value]) => (
                <FormControlLabel
                  key={key}
                  value={key}
                  control={<Radio />}
                  label={`${key}. ${value}`}
                  disabled={showAnswer}
                  sx={{
                    mb: 1,
                    p: 1,
                    borderRadius: 1,
                    ...(showAnswer && key === currentQuestion.correct_answer && {
                      backgroundColor: 'success.light',
                      color: 'success.contrastText',
                    }),
                    ...(showAnswer && selectedOption === key && key !== currentQuestion.correct_answer && {
                      backgroundColor: 'error.light',
                      color: 'error.contrastText',
                    }),
                  }}
                />
              ))}
            </RadioGroup>
          </FormControl>

          {showAnswer && (
            <Box mt={3} p={2} bgcolor="background.paper" borderRadius={1}>
              <Typography 
                variant="subtitle1" 
                color={isCorrect ? "success.main" : "error.main"}
                gutterBottom
                fontWeight="bold"
              >
                {isCorrect ? '정답입니다!' : '틀렸습니다.'}
              </Typography>
              <Typography variant="body2">
                정답: {currentQuestion.correct_answer}. {currentQuestion.options[currentQuestion.correct_answer]}
              </Typography>
              {currentQuestion.explanation && (
                <Typography variant="body2" mt={1}>
                  <strong>설명:</strong> {currentQuestion.explanation}
                </Typography>
              )}
            </Box>
          )}
        </CardContent>

        <Divider />

        <CardActions sx={{ justifyContent: 'space-between', p: 2 }}>
          <Button
            onClick={handleBack}
            disabled={activeStep === 0}
            startIcon={<NavigateBeforeIcon />}
          >
            이전 문제
          </Button>
          <Button
            variant="contained"
            color="primary"
            onClick={handleNext}
            disabled={!showAnswer && !selectedOption}
            endIcon={<NavigateNextIcon />}
          >
            {showAnswer ? '다음 문제' : '정답 확인'}
          </Button>
        </CardActions>
      </Card>
    </Container>
  );
};

export default QuestionPractice;