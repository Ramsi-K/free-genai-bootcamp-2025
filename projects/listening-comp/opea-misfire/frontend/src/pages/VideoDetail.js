import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
  Container, 
  Typography, 
  Paper, 
  Box,
  Grid,
  Card,
  CardContent,
  Button,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
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

// API endpoint configuration
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';
const QUESTION_API_URL = process.env.REACT_APP_QUESTION_API_URL || 'http://localhost:5001';
const AUDIO_API_URL = process.env.REACT_APP_AUDIO_API_URL || 'http://localhost:5002';

const VideoDetail = () => {
  const { videoId } = useParams();
  const navigate = useNavigate();
  const [videoData, setVideoData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingQuestions, setLoadingQuestions] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  const [existingQuestions, setExistingQuestions] = useState(null);

  useEffect(() => {
    fetchVideoData();
    checkExistingQuestions();
  }, [videoId]);

  const fetchVideoData = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/video/${videoId}`);
      setVideoData(response.data.data);
    } catch (err) {
      console.error('Error fetching video data:', err);
      setError('Failed to load video data. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const checkExistingQuestions = async () => {
    try {
      const response = await axios.get(`${QUESTION_API_URL}/api/questions/${videoId}`);
      if (response.data.success) {
        setExistingQuestions(response.data.data);
      }
    } catch (err) {
      // If 404, no questions exist yet - this is normal
      if (err.response?.status !== 404) {
        console.error('Error checking existing questions:', err);
      }
    }
  };

  const handleGenerateQuestions = async () => {
    setLoadingQuestions(true);
    setError(null);
    
    try {
      // First, index the video segments if not already done
      await axios.post(`${QUESTION_API_URL}/api/index-video/${videoId}`);
      
      // Then generate questions
      const response = await axios.post(`${QUESTION_API_URL}/api/generate-questions/${videoId}`, {
        num_questions: 5
      });
      
      // Process questions with audio
      await axios.post(`${AUDIO_API_URL}/api/process-questions/${videoId}`);
      
      setSuccess('문제가 생성되었습니다! 이제 듣기 연습을 시작할 수 있습니다.');
      setExistingQuestions(response.data);
      
      // Reload questions data
      await checkExistingQuestions();
    } catch (err) {
      console.error('Error generating questions:', err);
      setError(err.response?.data?.error || '문제 생성 중 오류가 발생했습니다.');
    } finally {
      setLoadingQuestions(false);
    }
  };

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <Container maxWidth="lg">
        <Box display="flex" justifyContent="center" my={4}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error && !videoData) {
    return (
      <Container maxWidth="lg">
        <Alert severity="error" sx={{ my: 2 }}>{error}</Alert>
        <Button 
          component={Link} 
          to="/videos" 
          startIcon={<ArrowBackIcon />}
        >
          비디오 목록으로 돌아가기
        </Button>
      </Container>
    );
  }

  const { metadata, segments = [] } = videoData || {};

  return (
    <Container maxWidth="lg">
      <Box mb={4}>
        <Button 
          component={Link} 
          to="/videos" 
          startIcon={<ArrowBackIcon />}
          sx={{ mb: 2 }}
        >
          비디오 목록으로 돌아가기
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
                {metadata?.title || '제목 없음'}
              </Typography>
              <Typography variant="subtitle1" color="textSecondary" gutterBottom>
                {metadata?.author || '알 수 없는 저자'}
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
                  YouTube에서 보기
                </Button>
                
                {existingQuestions ? (
                  <Button 
                    variant="contained"
                    color="primary"
                    startIcon={<HearingIcon />}
                    component={Link}
                    to={`/practice/${videoId}`}
                  >
                    듣기 연습 시작하기
                  </Button>
                ) : (
                  <Button 
                    variant="contained"
                    color="primary"
                    startIcon={<QuizIcon />}
                    onClick={handleGenerateQuestions}
                    disabled={loadingQuestions}
                  >
                    {loadingQuestions ? (
                      <>
                        <CircularProgress size={20} sx={{ mr: 1 }} />
                        문제 생성 중...
                      </>
                    ) : '듣기 문제 생성하기'}
                  </Button>
                )}
              </Box>
              
              <Grid container spacing={2}>
                <Grid item xs={6} sm={4}>
                  <Typography variant="body2" color="textSecondary">
                    비디오 길이:
                  </Typography>
                  <Typography variant="body1">
                    {metadata?.length ? `${Math.floor(metadata.length / 60)}분 ${metadata.length % 60}초` : '알 수 없음'}
                  </Typography>
                </Grid>
                <Grid item xs={6} sm={4}>
                  <Typography variant="body2" color="textSecondary">
                    세그먼트 수:
                  </Typography>
                  <Typography variant="body1">
                    {segments.length}
                  </Typography>
                </Grid>
                <Grid item xs={6} sm={4}>
                  <Typography variant="body2" color="textSecondary">
                    출판일:
                  </Typography>
                  <Typography variant="body1">
                    {metadata?.publish_date ? new Date(metadata.publish_date).toLocaleDateString('ko-KR') : '알 수 없음'}
                  </Typography>
                </Grid>
              </Grid>
            </Grid>
          </Grid>
        </Paper>

        <Tabs value={tabValue} onChange={handleTabChange} sx={{ mb: 2 }}>
          <Tab icon={<TextSnippetIcon />} label="스크립트" />
          <Tab icon={<InfoIcon />} label="세그먼트 정보" />
          {existingQuestions && <Tab icon={<QuizIcon />} label="문제 미리보기" />}
        </Tabs>

        {tabValue === 0 && (
          <Paper elevation={2} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              전체 스크립트
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
              {videoData?.full_transcript || '스크립트를 불러올 수 없습니다.'}
            </Typography>
          </Paper>
        )}

        {tabValue === 1 && (
          <Paper elevation={2} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              세그먼트 정보 ({segments.length}개)
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            {segments.map((segment, index) => (
              <Accordion key={index}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography>
                    세그먼트 {index + 1} ({formatTime(segment.start)} - {formatTime(segment.end)})
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    길이: {segment.duration.toFixed(1)}초
                  </Typography>
                  <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                    {segment.text}
                  </Typography>
                </AccordionDetails>
              </Accordion>
            ))}
          </Paper>
        )}

        {tabValue === 2 && existingQuestions && (
          <Paper elevation={2} sx={{ p: 3 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">
                생성된 문제 ({existingQuestions.questions.length}개)
              </Typography>
              <Button 
                variant="contained"
                color="primary"
                startIcon={<HearingIcon />}
                component={Link}
                to={`/practice/${videoId}`}
              >
                듣기 연습 시작하기
              </Button>
            </Box>
            <Divider sx={{ mb: 2 }} />
            
            <List>
              {existingQuestions.questions.map((question, index) => (
                <ListItem key={index} sx={{ display: 'block', mb: 2 }}>
                  <Paper elevation={1} sx={{ p: 2 }}>
                    <Typography variant="subtitle1" gutterBottom>
                      {index + 1}. {question.question}
                    </Typography>
                    <Box sx={{ pl: 2, mb: 2 }}>
                      {Object.entries(question.options).map(([key, value]) => (
                        <Typography 
                          key={key} 
                          variant="body2" 
                          sx={{ 
                            mb: 0.5,
                            fontWeight: key === question.correct_answer ? 'bold' : 'normal',
                            color: key === question.correct_answer ? 'success.main' : 'text.primary'
                          }}
                        >
                          {key}. {value}
                          {key === question.correct_answer && (
                            <Chip 
                              size="small" 
                              label="정답" 
                              color="success" 
                              sx={{ ml: 1 }} 
                            />
                          )}
                        </Typography>
                      ))}
                    </Box>
                    <Typography variant="body2" color="textSecondary">
                      세그먼트 시간: {formatTime(question.segment?.start)} - {formatTime(question.segment?.end)}
                    </Typography>
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
      >
        <Alert severity="error" variant="filled">
          {error}
        </Alert>
      </Snackbar>

      <Snackbar 
        open={success !== null} 
        autoHideDuration={6000} 
        onClose={() => setSuccess(null)}
      >
        <Alert severity="success" variant="filled">
          {success}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default VideoDetail;
