import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
  Container, 
  Typography, 
  Paper, 
  TextField, 
  Button, 
  Box,
  Grid,
  Card,
  CardContent,
  CardMedia,
  CircularProgress,
  Alert,
  Snackbar 
} from '@mui/material';
import YouTubeIcon from '@mui/icons-material/YouTube';
import HearingIcon from '@mui/icons-material/Hearing';

// API endpoint configuration
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';

const Home = () => {
  const navigate = useNavigate();
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/process`, {
        url: youtubeUrl
      });
      
      setSuccess(true);
      setYoutubeUrl('');
      
      // Navigate to the video detail page after processing
      setTimeout(() => {
        navigate(`/videos/${response.data.video_id}`);
      }, 1500);
    } catch (err) {
      console.error('Error processing video:', err);
      setError(err.response?.data?.error || 'Failed to process video. Please try another URL.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="lg">
      <Box my={4} textAlign="center">
        <Typography variant="h3" component="h1" gutterBottom>
          한국어 듣기 연습 앱
        </Typography>
        <Typography variant="h5" color="textSecondary" paragraph>
          Korean Listening Practice App
        </Typography>
      </Box>

      <Paper elevation={3} sx={{ p: 4, mb: 4 }}>
        <Typography variant="h5" gutterBottom>
          유튜브 비디오로 듣기 연습 생성하기
          <Typography variant="subtitle1" color="textSecondary">
            Create Listening Practice from YouTube Videos
          </Typography>
        </Typography>
        <Typography variant="body1" paragraph>
          한국어 콘텐츠가 포함된 YouTube 비디오 URL을 입력하세요. 비디오의 자막을 분석하여 TOPIK 스타일의 듣기 문제를 생성합니다.
          <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
            Enter a YouTube video URL containing Korean content. The system will analyze the subtitles and generate TOPIK-style listening comprehension questions.
          </Typography>
        </Typography>
        
        <form onSubmit={handleSubmit}>
          <TextField
            fullWidth
            label="YouTube URL"
            variant="outlined"
            value={youtubeUrl}
            onChange={(e) => setYoutubeUrl(e.target.value)}
            placeholder="https://www.youtube.com/watch?v=..."
            margin="normal"
            required
            disabled={loading}
            InputProps={{
              startAdornment: <YouTubeIcon color="error" sx={{ mr: 1 }} />,
            }}
          />
          
          <Box mt={2} display="flex" justifyContent="center">
            <Button 
              type="submit" 
              variant="contained" 
              color="primary" 
              size="large"
              disabled={loading || !youtubeUrl}
              startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <HearingIcon />}
            >
              {loading ? '처리 중...' : '비디오 처리하기'}
            </Button>
          </Box>
        </form>
      </Paper>

      <Grid container spacing={4}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardMedia
              component="img"
              height="140"
              image="/images/listening-practice.jpg"
              alt="Listening Practice"
              sx={{ objectFit: 'cover' }}
            />
            <CardContent>
              <Typography gutterBottom variant="h5" component="div">
                TOPIK 스타일 듣기 문제
                <Typography variant="subtitle1" color="textSecondary">
                  TOPIK-Style Listening Questions
                </Typography>
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                YouTube 비디오에서 추출한 콘텐츠를 바탕으로 실제 TOPIK 시험과 유사한 듣기 문제를 자동으로 생성합니다.
                <br /><br />
                Automatically generates listening comprehension questions similar to real TOPIK exams based on content extracted from YouTube videos.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardMedia
              component="img"
              height="140"
              image="/images/korean-language.jpg"
              alt="Korean Language"
              sx={{ objectFit: 'cover' }}
            />
            <CardContent>
              <Typography gutterBottom variant="h5" component="div">
                맞춤형 학습 경험
                <Typography variant="subtitle1" color="textSecondary">
                  Customized Learning Experience
                </Typography>
              </Typography>
              <Typography variant="body2" color="text.secondary">
                관심 있는 주제의 YouTube 비디오를 선택하여 학습할 수 있습니다.
                <br />
                Choose YouTube videos on topics that interest you.
                <br /><br />
                다양한 난이도와 주제의 콘텐츠를 통해 한국어 듣기 실력을 향상시키세요.
                <br />
                Improve your Korean listening skills through content of various difficulties and topics.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

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
        open={success} 
        autoHideDuration={6000} 
        onClose={() => setSuccess(false)}
      >
        <Alert severity="success" variant="filled">
          비디오 처리가 완료되었습니다!
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default Home;
