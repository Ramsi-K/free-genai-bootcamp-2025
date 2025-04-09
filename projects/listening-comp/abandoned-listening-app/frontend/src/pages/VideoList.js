import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Container, Typography, Paper, Box, Grid, Card, CardContent, 
  CardMedia, CardActions, Button, CircularProgress, Alert, 
  Divider, IconButton, Tooltip, Chip
} from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import DeleteIcon from '@mui/icons-material/Delete';
import VideoLibraryIcon from '@mui/icons-material/VideoLibrary';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import QuizIcon from '@mui/icons-material/Quiz';
import { useAppContext } from '../context/AppContext';
import { videoAPI } from '../services/api';

const VideoList = () => {
  const { state, actions } = useAppContext();
  const { videoList, loading, error } = state;

  useEffect(() => {
    fetchVideos();
  }, []);

  const fetchVideos = async () => {
    try {
      actions.startLoading();
      actions.clearError();
      const response = await videoAPI.getAll();
      if (response.data.success) {
        actions.setVideoList(response.data.videos);
      }
    } catch (err) {
      actions.setError(err.message || 'Failed to load videos');
    } finally {
      actions.stopLoading();
    }
  };

  const handleDeleteVideo = async (videoId, e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (window.confirm('이 비디오를 삭제하시겠습니까?')) {
      try {
        actions.startLoading();
        await videoAPI.delete(videoId);
        actions.setVideoList(videoList.filter(v => v.video_id !== videoId));
      } catch (err) {
        actions.setError('비디오 삭제 중 오류가 발생했습니다.');
      } finally {
        actions.stopLoading();
      }
    }
  };

  const formatDate = (timestamp) => {
    if (!timestamp) return 'Unknown';
    return new Date(timestamp * 1000).toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <Container maxWidth="lg">
      <Box display="flex" alignItems="center" mb={3}>
        <Button 
          component={Link} 
          to="/" 
          startIcon={<ArrowBackIcon />}
          sx={{ mr: 2 }}
        >
          뒤로 가기
        </Button>
        <Typography variant="h4" component="h1">
          처리된 비디오 목록
        </Typography>
      </Box>

      {loading ? (
        <Box display="flex" justifyContent="center" my={4}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error" sx={{ my: 2 }}>{error}</Alert>
      ) : videoList.length === 0 ? (
        <Paper elevation={2} sx={{ p: 3, textAlign: 'center' }}>
          <VideoLibraryIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            처리된 비디오가 없습니다
          </Typography>
          <Typography variant="body2" color="textSecondary" paragraph>
            홈 페이지로 돌아가서 YouTube URL을 추가하여 새 비디오를 처리하세요.
          </Typography>
          <Button 
            component={Link} 
            to="/" 
            variant="contained" 
            color="primary"
          >
            비디오 추가하기
          </Button>
        </Paper>
      ) : (
        <Grid container spacing={3}>
          {videoList.map((video) => (
            <Grid item xs={12} sm={6} md={4} key={video.video_id}>
              <Card 
                sx={{ 
                  height: '100%', 
                  display: 'flex', 
                  flexDirection: 'column',
                  textDecoration: 'none',
                  '&:hover': { 
                    boxShadow: 6
                  }
                }}
              >
                <CardMedia
                  component="img"
                  height="140"
                  image={`https://img.youtube.com/vi/${video.video_id}/mqdefault.jpg`}
                  alt={video.title}
                />
                <CardContent sx={{ flexGrow: 1 }}>
                  <Typography variant="h6" component="div" gutterBottom noWrap>
                    {video.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    세그먼트 수: {video.segments_count}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    처리 날짜: {formatDate(video.processed_date)}
                  </Typography>
                </CardContent>
                <Divider />
                <CardActions>
                  <Button 
                    component={Link}
                    to={`/videos/${video.video_id}`}
                    size="small" 
                    startIcon={<PlayArrowIcon />}
                  >
                    상세 보기
                  </Button>
                  <Button 
                    component={Link}
                    to={`/practice/${video.video_id}`}
                    size="small" 
                    color="primary"
                    startIcon={<QuizIcon />}
                  >
                    문제 풀기
                  </Button>
                  <Box flexGrow={1} />
                  <Tooltip title="비디오 삭제">
                    <IconButton 
                      color="error" 
                      size="small"
                      onClick={(e) => handleDeleteVideo(video.video_id, e)}
                    >
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Container>
  );
};

export default VideoList;