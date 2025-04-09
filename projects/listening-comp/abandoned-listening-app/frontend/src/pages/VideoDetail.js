import React, { useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  Container, Typography, Paper, Box, Grid, Card, 
  CardContent, Button, Alert
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import HearingIcon from '@mui/icons-material/Hearing';
import LoadingSpinner from '../components/LoadingSpinner';
import AudioPlayer from '../components/AudioPlayer';
import { useAppContext } from '../context/AppContext';
import { videoAPI, questionAPI } from '../services/api';
import { withRetry } from '../utils/retryUtil';

const VideoDetail = () => {
  const { videoId } = useParams();
  const { state, actions } = useAppContext();
  const { currentVideo, loading, error } = state;

  useEffect(() => {
    loadVideoDetails();
  }, [videoId]);

  const loadVideoDetails = async () => {
    try {
      actions.startLoading();
      actions.clearError();
      
      const [videoResponse, questionsResponse] = await Promise.all([
        withRetry(() => videoAPI.getById(videoId)),
        withRetry(() => questionAPI.getByVideo(videoId))
      ]);

      if (videoResponse.data.success) {
        actions.setCurrentVideo({
          ...videoResponse.data,
          questions: questionsResponse.data.questions
        });
      }
    } catch (err) {
      actions.setError(err.message);
    } finally {
      actions.stopLoading();
    }
  };

  if (loading) return <LoadingSpinner message="비디오 정보를 불러오는 중..." />;
  if (error) return <Alert severity="error">{error}</Alert>;
  if (!currentVideo) return <Alert severity="info">비디오를 찾을 수 없습니다.</Alert>;

  return (
    <Container maxWidth="lg">
      <Box mb={4}>
        <Button
          component={Link}
          to="/videos"
          startIcon={<ArrowBackIcon />}
          sx={{ mb: 2 }}
        >
          목록으로 돌아가기
        </Button>

        <Paper elevation={3} sx={{ p: 3 }}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <img
                src={`https://img.youtube.com/vi/${videoId}/mqdefault.jpg`}
                alt={currentVideo.title}
                style={{ width: '100%', borderRadius: '4px' }}
              />
            </Grid>
            <Grid item xs={12} md={8}>
              <Typography variant="h4" gutterBottom>
                {currentVideo.title}
              </Typography>
              
              <Box my={2}>
                <Button
                  variant="contained"
                  color="primary"
                  component={Link}
                  to={`/practice/${videoId}`}
                  startIcon={<HearingIcon />}
                  disabled={!currentVideo.questions?.length}
                >
                  듣기 연습 시작하기
                </Button>
              </Box>

              {currentVideo.questions?.map((question, index) => (
                <Card key={index} sx={{ mb: 2 }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      문제 {index + 1}
                    </Typography>
                    <Typography variant="body1" gutterBottom>
                      {question.question}
                    </Typography>
                    {question.audio_url && (
                      <AudioPlayer 
                        src={questionAPI.getAudio(question.audio_url)}
                        onEnded={() => console.log('Audio ended')}
                      />
                    )}
                  </CardContent>
                </Card>
              ))}
            </Grid>
          </Grid>
        </Paper>
      </Box>
    </Container>
  );
};

export default VideoDetail;
