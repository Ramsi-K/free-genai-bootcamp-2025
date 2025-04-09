import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { TextField, Button, Container, Typography, Box, CircularProgress } from '@mui/material';
import axios from 'axios';

// Use environment variable for API base URL, default to localhost:8000
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

function HomePage() {
    const [videoUrl, setVideoUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (event) => {
        event.preventDefault();
        setLoading(true);
        setError('');

        if (!videoUrl) {
            setError('Please enter a YouTube video URL.');
            setLoading(false);
            return;
        }

        try {
            // Call the consolidated backend endpoint
            const response = await axios.post(`${API_BASE_URL}/api/process`, {
                url: videoUrl,
                // num_questions: 3 // Optional: Add if you want to specify number of questions
            });

            if (response.data.success) {
                const videoId = response.data.video_id;
                // Navigate to the video detail page after successful processing
                navigate(`/video/${videoId}`);
            } else {
                setError(response.data.error || 'Failed to process video. Please check the URL and try again.');
            }
        } catch (err) {
            console.error("Error processing video:", err);
            let errorMessage = 'An error occurred while processing the video.';
            if (err.response && err.response.data && err.response.data.error) {
                errorMessage = err.response.data.error;
            } else if (err.message) {
                errorMessage = err.message;
            }
            setError(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Container maxWidth="sm">
            <Box sx={{ my: 4, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <Typography variant="h4" component="h1" gutterBottom>
                    Korean Listening Practice
                </Typography>
                <Typography variant="subtitle1" gutterBottom>
                    Enter a YouTube video URL to generate practice questions.
                </Typography>
                <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1, width: '100%' }}>
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
                        onChange={(e) => setVideoUrl(e.target.value)}
                        disabled={loading}
                    />
                    {error && (
                        <Typography color="error" variant="body2" sx={{ mt: 1 }}>
                            {error}
                        </Typography>
                    )}
                    <Button
                        type="submit"
                        fullWidth
                        variant="contained"
                        sx={{ mt: 3, mb: 2 }}
                        disabled={loading}
                    >
                        {loading ? <CircularProgress size={24} /> : 'Generate Questions'}
                    </Button>
                </Box>
            </Box>
        </Container>
    );
}

export default HomePage;