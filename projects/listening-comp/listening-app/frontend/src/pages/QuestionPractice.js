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
  Card,
  CardContent,
  CardActions,
  Stepper,
  Step,
  StepLabel,
  IconButton,
  CircularProgress,
  Alert,
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

// API endpoint configuration - Point only to the main backend
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

const QuestionPractice = () => {
  const { videoId } = useParams();
  const navigate = useNavigate();
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeStep, setActiveStep] = useState(0);
  const [selectedChoiceIndex, setSelectedChoiceIndex] = useState(null); // Store index (0-3)
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
    setLoading(true);
    setError(null);
    try {
      // Fetch questions directly from the main backend
      const response = await axios.get(`${API_BASE_URL}/api/questions/${videoId}`);

      if (response.data.success && response.data.questions && response.data.questions.length > 0) {
        // Ensure choices are parsed if they are still JSON strings (though backend should handle this)
        const parsedQuestions = response.data.questions.map(q => ({
          ...q,
          choices: typeof q.choices === 'string' ? JSON.parse(q.choices) : q.choices
        }));
        setQuestions(parsedQuestions);
        setVideoTitle(response.data.video_title || ''); // Get title from the same response
      } else if (response.data.success && response.data.questions.length === 0) {
        setError('No questions found for this video. Please generate them first.');
        setQuestions([]); // Ensure questions are empty
      } else {
        throw new Error(response.data.error || 'Failed to load questions.');
      }
    } catch (err) {
      console.error('Error fetching questions:', err);
      let errorMessage = 'An error occurred while fetching questions.';
      if (err.response && err.response.data && err.response.data.error) {
        errorMessage = err.response.data.error;
      } else if (err.message) {
        errorMessage = err.message;
      }
      setError(errorMessage);
      setQuestions([]); // Ensure questions are empty on error
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    if (showAnswer) {
      setActiveStep((prevActiveStep) => prevActiveStep + 1);
      setSelectedChoiceIndex(null); // Reset selected index
      setShowAnswer(false);
      setAudioPlaying(false);
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
      }
    } else {
      checkAnswer();
    }
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
    setSelectedChoiceIndex(null); // Reset selected index
    setShowAnswer(false);
    setAudioPlaying(false);
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
  };

  const checkAnswer = () => {
    if (selectedChoiceIndex === null) {
      return; // Don't check if no option is selected
    }

    const currentQuestion = questions[activeStep];
    const correctAnswerIndex = currentQuestion.correct_answer; // Backend provides 0-3 index
    const correct = selectedChoiceIndex === correctAnswerIndex;

    setIsCorrect(correct);
    setShowAnswer(true);

    if (correct) {
      setScore(prevScore => prevScore + 1);
    }
  };

  const handleOptionChange = (event) => {
    setSelectedChoiceIndex(parseInt(event.target.value, 10)); // Store the choice index (0-3)
  };

  const handlePlayAudio = () => {
    const currentQuestion = questions[activeStep];
    const audioPath = currentQuestion.audio_url; // e.g., /api/audio/videoID_q1.wav

    if (audioRef.current && audioPath) {
      const fullAudioUrl = `${API_BASE_URL}${audioPath}`;
      if (audioPlaying) {
        audioRef.current.pause();
        setAudioPlaying(false);
      } else {
        if (audioRef.current.src !== fullAudioUrl) {
          audioRef.current.src = fullAudioUrl;
        }
        audioRef.current.play().catch(e => console.error("Audio play error:", e));
        setAudioPlaying(true);
      }
    } else {
      console.warn("Audio ref not ready or no audio URL for question");
    }
  };

  const handleAudioEnded = () => {
    setAudioPlaying(false);
  };

  const restartPractice = () => {
    setActiveStep(0);
    setSelectedChoiceIndex(null);
    setShowAnswer(false);
    setScore(0);
    setProgress(0);
    setAudioPlaying(false);
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current.src = ''; // Clear src on restart
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
          to={`/video/${videoId}`}
          startIcon={<ArrowBackIcon />}
          sx={{ mr: 2 }}
        >
          Return to Video Details
        </Button>
        <Button
          component={Link}
          to="/"
          startIcon={<HomeIcon />}
        >
          Return Home
        </Button>
      </Container>
    );
  }

  if (questions.length === 0 && !loading) {
    return (
      <Container maxWidth="md">
        <Alert severity="info" sx={{ my: 2 }}>
          No questions available for this video.
        </Alert>
        <Button
          component={Link}
          to={`/video/${videoId}`}
          startIcon={<ArrowBackIcon />}
        >
          Return to Video Details
        </Button>
      </Container>
    );
  }

  if (activeStep === questions.length) {
    return (
      <Container maxWidth="md">
        <Paper elevation={3} sx={{ p: 4, my: 4, textAlign: 'center' }}>
          <CheckCircleIcon color="success" sx={{ fontSize: 80, mb: 2 }} />
          <Typography variant="h4" gutterBottom>
            Practice Complete!
          </Typography>
          <Typography variant="h5" color="primary" gutterBottom>
            Score: {score} / {questions.length} ({questions.length > 0 ? Math.round((score / questions.length) * 100) : 0}%)
          </Typography>
          <Typography variant="body1" paragraph>
            {score === questions.length ?
              'Perfect! You answered all questions correctly.' :
              'Good job! Keep practicing to improve further.'}
          </Typography>
          <Box display="flex" justifyContent="center" mt={3}>
            <Button
              variant="outlined"
              startIcon={<HomeIcon />}
              component={Link}
              to="/"
              sx={{ mr: 2 }}
            >
              Back to Home
            </Button>
            <Button
              variant="contained"
              color="primary"
              startIcon={<ReplayIcon />}
              onClick={restartPractice}
            >
              Practice Again
            </Button>
          </Box>
        </Paper>
      </Container>
    );
  }

  const currentQuestion = questions[activeStep];
  const audioPath = currentQuestion.audio_url;

  return (
    <Container maxWidth="md">
      <Box mb={2} display="flex" alignItems="center">
        <Button
          component={Link}
          to={`/video/${videoId}`}
          startIcon={<ArrowBackIcon />}
          sx={{ mr: 2 }}
        >
          Back to Details
        </Button>
        <Typography variant="h5" sx={{ flexGrow: 1 }}>
          Listening Practice
        </Typography>
        <Typography variant="body2" color="textSecondary">
          Score: {score} / {activeStep + (showAnswer ? 1 : 0)}
        </Typography>
      </Box>

      {videoTitle && (
        <Typography variant="subtitle1" color="textSecondary" gutterBottom>
          Video: {videoTitle}
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
              disabled={!audioPath}
              size="large"
            >
              {audioPlaying ? "Listening..." : "Play Question Audio"}
            </Button>
            <audio
              ref={audioRef}
              onEnded={handleAudioEnded}
              onError={(e) => console.error('Audio Error:', e)}
              style={{ display: 'none' }}
              preload="none"
            />
          </Box>

          <Typography variant="h6" gutterBottom>
            Question {activeStep + 1}: {currentQuestion.question_text}
          </Typography>

          <FormControl component="fieldset" sx={{ mt: 2, width: '100%' }}>
            <RadioGroup
              name="question-options"
              value={selectedChoiceIndex !== null ? selectedChoiceIndex.toString() : ''}
              onChange={handleOptionChange}
            >
              {Array.isArray(currentQuestion.choices) && currentQuestion.choices.map((choiceText, index) => (
                <FormControlLabel
                  key={index}
                  value={index.toString()}
                  control={<Radio />}
                  label={`${index + 1}. ${choiceText}`}
                  disabled={showAnswer}
                  sx={{
                    mb: 1,
                    p: 1,
                    borderRadius: 1,
                    ...(showAnswer && index === currentQuestion.correct_answer && {
                      backgroundColor: 'success.light',
                      color: 'success.contrastText',
                      fontWeight: 'bold'
                    }),
                    ...(showAnswer && selectedChoiceIndex === index && index !== currentQuestion.correct_answer && {
                      backgroundColor: 'error.light',
                      color: 'error.contrastText',
                      textDecoration: 'line-through'
                    }),
                  }}
                />
              ))}
            </RadioGroup>
          </FormControl>

          {showAnswer && (
            <Box mt={3} p={2} bgcolor={isCorrect ? 'success.lighter' : 'error.lighter'} borderRadius={1}>
              <Typography
                variant="subtitle1"
                color={isCorrect ? "success.main" : "error.main"}
                gutterBottom
                fontWeight="bold"
              >
                {isCorrect ? 'Correct!' : 'Incorrect.'}
              </Typography>
              <Typography variant="body2">
                Correct Answer: {currentQuestion.correct_answer + 1}. {currentQuestion.choices[currentQuestion.correct_answer]}
              </Typography>
              {currentQuestion.audio_segment && (
                <Typography variant="body2" mt={1} fontStyle='italic'>
                  Related Transcript: "{currentQuestion.audio_segment}"
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
            Previous
          </Button>
          <Button
            variant="contained"
            color="primary"
            onClick={handleNext}
            disabled={!showAnswer && selectedChoiceIndex === null}
            endIcon={<NavigateNextIcon />}
          >
            {showAnswer ? 'Next Question' : 'Check Answer'}
          </Button>
        </CardActions>
      </Card>
    </Container>
  );
};

export default QuestionPractice;