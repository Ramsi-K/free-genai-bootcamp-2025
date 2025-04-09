import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
    TextField, Button, Container, Typography, Box, 
    CircularProgress, FormControl, InputLabel, Select, 
    MenuItem, Alert, Paper
} from '@mui/material';
import YouTubeIcon from '@mui/icons-material/YouTube';
import { useAppContext } from '../context/AppContext';
import { videoAPI } from '../services/api';
import { withRetry } from '../utils/retryUtil';

const YOUTUBE_URL_REGEX = /^(https?:\/\/)?(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/)[a-zA-Z0-9_-]{11}$/;

function HomePage() {
    const [videoUrl, setVideoUrl] = useState('');
    const [urlError, setUrlError] = useState('');
    const [level, setLevel] = useState('intermediate');
    const { state, actions } = useAppContext();
    const navigate = useNavigate();

    const validateUrl = (url) => {
        if (!url) {
            setUrlError('URL을 입력해주세요.');
            return false;
        }
        if (!YOUTUBE_URL_REGEX.test(url)) {
            setUrlError('올바른 YouTube URL을 입력해주세요.');
            return false;
        }
        setUrlError('');
        return true;
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        if (!validateUrl(videoUrl)) return;

        try {
            actions.startLoading();
            actions.clearError();

            const response = await withRetry(() => 
                videoAPI.process(videoUrl, level)
            );

            if (response.data.success) {
                const { video_id } = response.data;
                navigate(`/video/${video_id}`);
            }
        } catch (err) {
            actions.setError(err.message || '비디오 처리 중 오류가 발생했습니다.');
        } finally {
            actions.stopLoading();
        }
    };

    return (
        <Container maxWidth="sm">
            <Box sx={{ 
                my: 4, 
                display: 'flex', 
                flexDirection: 'column', 
                alignItems: 'center' 
            }}>
                <YouTubeIcon sx={{ fontSize: 60, color: 'error.main', mb: 2 }} />
                <Typography variant="h4" component="h1" gutterBottom align="center">
                    한국어 듣기 연습
                </Typography>
                <Typography variant="subtitle1" gutterBottom align="center">
                    YouTube 비디오로 TOPIK 스타일 듣기 문제를 생성하세요.
                </Typography>

                <Paper elevation={3} sx={{ p: 3, width: '100%', mt: 3 }}>
                    <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%' }}>
                        <TextField
                            margin="normal"
                            required
                            fullWidth
                            id="videoUrl"
                            label="YouTube Video URL"
                            name="videoUrl"
                            autoComplete="url"
                            autoFocus
                            value={videoUrl}
                            onChange={(e) => {
                                setVideoUrl(e.target.value);
                                if (urlError) validateUrl(e.target.value);
                            }}
                            error={Boolean(urlError)}
                            helperText={urlError}
                            disabled={state.loading}
                        />

                        <FormControl fullWidth margin="normal">
                            <InputLabel id="level-select-label">난이도</InputLabel>
                            <Select
                                labelId="level-select-label"
                                id="level-select"
                                value={level}
                                label="난이도"
                                onChange={(e) => setLevel(e.target.value)}
                                disabled={state.loading}
                            >
                                <MenuItem value="beginner">초급 (TOPIK I)</MenuItem>
                                <MenuItem value="intermediate">중급 (TOPIK II)</MenuItem>
                                <MenuItem value="advanced">고급 (TOPIK II)</MenuItem>
                            </Select>
                        </FormControl>

                        {state.error && (
                            <Alert severity="error" sx={{ mt: 2 }}>
                                {state.error}
                            </Alert>
                        )}

                        <Button
                            type="submit"
                            fullWidth
                            variant="contained"
                            sx={{ mt: 3, mb: 2, py: 1.5 }}
                            disabled={state.loading}
                        >
                            {state.loading ? (
                                <CircularProgress size={24} />
                            ) : (
                                '문제 생성하기'
                            )}
                        </Button>
                    </Box>
                </Paper>
            </Box>
        </Container>
    );
}

export default HomePage;