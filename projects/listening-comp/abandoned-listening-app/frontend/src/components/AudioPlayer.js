import React, { useEffect, useRef, useState } from 'react';
import { Box, IconButton, LinearProgress } from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import PauseIcon from '@mui/icons-material/Pause';
import ReplayIcon from '@mui/icons-material/Replay';
import { useAppContext } from '../context/AppContext';

const AudioPlayer = ({ src, onEnded, autoPlayDelay = 0 }) => {
  const audioRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const { actions } = useAppContext();

  useEffect(() => {
    if (autoPlayDelay > 0) {
      const timer = setTimeout(() => {
        handlePlay();
      }, autoPlayDelay);
      return () => clearTimeout(timer);
    }
  }, [autoPlayDelay]);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const updateProgress = () => {
      const value = (audio.currentTime / audio.duration) * 100;
      setProgress(isNaN(value) ? 0 : value);
    };

    audio.addEventListener('timeupdate', updateProgress);
    audio.addEventListener('ended', handleEnded);
    audio.addEventListener('error', handleError);

    return () => {
      audio.removeEventListener('timeupdate', updateProgress);
      audio.removeEventListener('ended', handleEnded);
      audio.removeEventListener('error', handleError);
    };
  }, []);

  const handlePlay = () => {
    const audio = audioRef.current;
    if (audio) {
      audio.play()
        .then(() => {
          setIsPlaying(true);
          actions.setAudioPlaying(true);
        })
        .catch(handleError);
    }
  };

  const handlePause = () => {
    const audio = audioRef.current;
    if (audio) {
      audio.pause();
      setIsPlaying(false);
      actions.setAudioPlaying(false);
    }
  };

  const handleReplay = () => {
    const audio = audioRef.current;
    if (audio) {
      audio.currentTime = 0;
      handlePlay();
    }
  };

  const handleEnded = () => {
    setIsPlaying(false);
    actions.setAudioPlaying(false);
    if (onEnded) onEnded();
  };

  const handleError = (error) => {
    console.error('Audio playback error:', error);
    setIsPlaying(false);
    actions.setAudioPlaying(false);
    actions.setError('오디오 재생 중 오류가 발생했습니다.');
  };

  return (
    <Box sx={{ width: '100%', display: 'flex', alignItems: 'center', gap: 2 }}>
      <IconButton 
        onClick={isPlaying ? handlePause : handlePlay}
        color="primary"
        size="large"
      >
        {isPlaying ? <PauseIcon /> : <PlayArrowIcon />}
      </IconButton>
      <IconButton
        onClick={handleReplay}
        color="primary"
        size="large"
      >
        <ReplayIcon />
      </IconButton>
      <Box sx={{ flexGrow: 1 }}>
        <LinearProgress 
          variant="determinate" 
          value={progress} 
          sx={{ height: 8, borderRadius: 4 }}
        />
      </Box>
      <audio
        ref={audioRef}
        src={src}
        preload="auto"
        style={{ display: 'none' }}
      />
    </Box>
  );
};

export default AudioPlayer;