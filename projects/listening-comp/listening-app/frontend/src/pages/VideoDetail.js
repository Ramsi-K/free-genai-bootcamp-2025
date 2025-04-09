import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  Container,
  Typography,
  Paper,
  Box,
  Grid,
  Button,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  Chip,
  CircularProgress,
  Alert,
  Snackbar,
  Tabs,
  Tab
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import QuizIcon from '@mui/icons-material/Quiz';
import YouTubeIcon from '@mui/icons-material/YouTube';
import InfoIcon from '@mui/icons-material/Info';
import TextSnippetIcon from '@mui/icons-material/TextSnippet';
import HearingIcon from '@mui/icons-material/Hearing';

// API endpoint configuration - Point only to the main backend
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

const VideoDetail = () => {
  const { videoId } = useParams();
  const navigate = useNavigate();
  const [videoData, setVideoData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  const [existingQuestions, setExistingQuestions] = useState([]);
  const [questionsChecked, setQuestionsChecked] = useState(false);

  useEffect(() => {
    setLoading(true);
    setError(null);
    setVideoData(null);
    setExistingQuestions([]);
    setQuestionsChecked(false);
    setTabValue(0);

    const fetchData = async () => {
      try {
        const [videoDetailsResponse, questionsResponse] = await Promise.all([
          axios.get(`${API_BASE_URL}/api/video/${videoId}`),
          axios.get(`${API_BASE_URL}/api/questions/${videoId}`)
            .catch(err => {
              if (err.response && err.response.status === 404) {
                return { data: { success: true, questions: [] } };
              }
              throw err;
            })
        ]);

        if (videoDetailsResponse.data.success) {
          setVideoData(videoDetailsResponse.data.data);
        } else {
          throw new Error(videoDetailsResponse.data.error || 'Failed to load video data.');
        }

        if (questionsResponse.data.success) {
          setExistingQuestions(questionsResponse.data.questions || []);
        } else {
          console.warn('Could not retrieve existing questions:', questionsResponse.data.error);
          setExistingQuestions([]);
        }

      } catch (err) {
        console.error('Error fetching video details or questions:', err);
        let errorMessage = 'Failed to load video details or check questions.';
        if (err.response && err.response.data && err.response.data.error) {
          errorMessage = err.response.data.error;
        } else if (err.message) {
          errorMessage = err.message;
        }
        setError(errorMessage);
        setVideoData(null);
        setExistingQuestions([]);
      } finally {
        setLoading(false);
        setQuestionsChecked(true);
      }
    };

    fetchData();

  }, [videoId]);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const formatTime = (seconds) => {
    if (typeof seconds !== 'number' || isNaN(seconds)) return '0:00';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <Container maxWidth="lg">
        <Box display="flex" justifyContent="center" alignItems="center" sx={{ minHeight: '60vh' }}>
          <CircularProgress />
          <Typography sx={{ ml: 2 }}>Loading video details...</Typography>
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg">
        <Alert severity="error" sx={{ my: 2 }}>{error}</Alert>
        <Button
          component={Link}
          to="/"
          startIcon={<ArrowBackIcon />}
        >
          Return Home
        </Button>
      </Container>
    );
  }

  if (!videoData) {
    return (
      <Container maxWidth="lg">
        <Alert severity="warning" sx={{ my: 2 }}>Video data could not be loaded.</Alert>
        <Button
          component={Link}
          to="/"
          startIcon={<ArrowBackIcon />}
        >
          Return Home
        </Button>
      </Container>
    );
  }

  const { metadata = {}, segments = [] } = videoData;
  const hasQuestions = existingQuestions && existingQuestions.length > 0;

  return (
    <Container maxWidth="lg">
      <Box mb={4}>
        <Button
          component={Link}
          to="/"
          startIcon={<ArrowBackIcon />}
          sx={{ mb: 2 }}
        >
          Return Home
        </Button>

        <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Box
                component="img"
                src={`https://img.youtube.com/vi/${videoId}/mqdefault.jpg`}
                alt={metadata?.title}
                sx={{ width: '100%', borderRadius: 1 }}
              />
            </Grid>
            <Grid item xs={12} md={8}>
              <Typography variant="h4" gutterBottom>
                {metadata?.title || 'Video Title Unavailable'}
              </Typography>
              <Typography variant="subtitle1" color="textSecondary" gutterBottom>
                {metadata?.author || 'Author Unknown'}
              </Typography>
              <Box display="flex" alignItems="center" mb={2}>
                <Button
                  variant="outlined"
                  startIcon={<YouTubeIcon />}
                  href={`https://www.youtube.com/watch?v=${videoId}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  sx={{ mr: 2 }}
                >
                  Watch on YouTube
                </Button>

                {questionsChecked && hasQuestions && (
                  <Button
                    variant="contained"
                    color="primary"
                    startIcon={<HearingIcon />}
                    component={Link}
                    to={`/practice/${videoId}`}
                  >
                    Start Listening Practice
                  </Button>
                )}
                {questionsChecked && !hasQuestions && (
                  <Typography variant="body2" color="text.secondary">
                    Listening practice questions are not yet available for this video.
                    Go back home to process a video.
                  </Typography>
                )}
                {!questionsChecked && (
                  <Box display="flex" alignItems="center">
                    <CircularProgress size={20} sx={{ mr: 1 }} />
                    <Typography variant="body2" color="text.secondary">Checking for questions...</Typography>
                  </Box>
                )}
              </Box>

              <Grid container spacing={2}>
                <Grid item xs={6} sm={4}>
                  <Typography variant="body2" color="textSecondary">
                    Video Length:
                  </Typography>
                  <Typography variant="body1">
                    {metadata?.length ? `${Math.floor(metadata.length / 60)}m ${metadata.length % 60}s` : 'N/A'}
                  </Typography>
                </Grid>
                <Grid item xs={6} sm={4}>
                  <Typography variant="body2" color="textSecondary">
                    Segments:
                  </Typography>
                  <Typography variant="body1">
                    {segments.length}
                  </Typography>
                </Grid>
                <Grid item xs={6} sm={4}>
                  <Typography variant="body2" color="textSecondary">
                    Published:
                  </Typography>
                  <Typography variant="body1">
                    {metadata?.publish_date ? new Date(metadata.publish_date).toLocaleDateString('en-CA') : 'N/A'}
                  </Typography>
                </Grid>
              </Grid>
            </Grid>
          </Grid>
        </Paper>

        <Tabs value={tabValue} onChange={handleTabChange} sx={{ mb: 2 }}>
          <Tab icon={<TextSnippetIcon />} label="Transcript" />
          <Tab icon={<InfoIcon />} label="Segments" />
          {hasQuestions && <Tab icon={<QuizIcon />} label="Questions Preview" />}
        </Tabs>

        {tabValue === 0 && (
          <Paper elevation={2} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Full Transcript
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', maxHeight: '400px', overflowY: 'auto' }}>
              {metadata?.transcript || 'Transcript not available.'}
            </Typography>
          </Paper>
        )}

        {tabValue === 1 && (
          <Paper elevation={2} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Segments ({segments.length})
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Box sx={{ maxHeight: '400px', overflowY: 'auto' }}>
              {segments.map((segment, index) => (
                <Accordion key={segment.id || index}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography>
                      Segment {index + 1} ({formatTime(segment.start)} - {formatTime(segment.end)})
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography variant="body2" color="textSecondary" gutterBottom>
                      Duration: {segment.duration?.toFixed(1)}s
                    </Typography>
                    <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                      {segment.text}
                    </Typography>
                  </AccordionDetails>
                </Accordion>
              ))}
            </Box>
          </Paper>
        )}

        {tabValue === 2 && hasQuestions && (
          <Paper elevation={2} sx={{ p: 3 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">
                Generated Questions ({existingQuestions.length})
              </Typography>
              <Button
                variant="contained"
                color="primary"
                startIcon={<HearingIcon />}
                component={Link}
                to={`/practice/${videoId}`}
              >
                Start Listening Practice
              </Button>
            </Box>
            <Divider sx={{ mb: 2 }} />

            <List>
              {existingQuestions.map((question, index) => (
                <ListItem key={question.id || index} sx={{ display: 'block', mb: 2 }}>
                  <Paper elevation={1} sx={{ p: 2 }}>
                    <Typography variant="subtitle1" gutterBottom>
                      {index + 1}. {question.question_text}
                    </Typography>
                    <Box sx={{ pl: 2, mb: 1 }}>
                      {Array.isArray(question.choices) && question.choices.map((choice, choiceIndex) => (
                        <Typography
                          key={choiceIndex}
                          variant="body2"
                          sx={{
                            mb: 0.5,
                            fontWeight: choiceIndex === question.correct_answer ? 'bold' : 'normal',
                            color: choiceIndex === question.correct_answer ? 'success.main' : 'text.primary'
                          }}
                        >
                          {choiceIndex + 1}. {choice}
                          {choiceIndex === question.correct_answer && (
                            <Chip
                              size="small"
                              label="Correct"
                              color="success"
                              sx={{ ml: 1 }}
                            />
                          )}
                        </Typography>
                      ))}
                    </Box>
                    {question.audio_segment && (
                      <Typography variant="caption" color="textSecondary" display="block" sx={{ mt: 1, fontStyle: 'italic' }}>
                        Related Transcript: "{question.audio_segment}"
                      </Typography>
                    )}
                    {question.audio_url && (
                      <Typography variant="caption" color="textSecondary" display="block" sx={{ mt: 1 }}>
                        (Audio available for practice)
                      </Typography>
                    )}
                  </Paper>
                </ListItem>
              ))}
            </List>
          </Paper>
        )}
      </Box>

      <Snackbar
        open={error !== null}
        autoHideDuration={6000}
        onClose={() => setError(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert severity="error" variant="filled" onClose={() => setError(null)}>
          {error}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default VideoDetail;
