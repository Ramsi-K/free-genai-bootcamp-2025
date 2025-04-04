import React from 'react';
import { Link } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import HearingIcon from '@mui/icons-material/Hearing';
import VideoLibraryIcon from '@mui/icons-material/VideoLibrary';

const AppHeader = () => {
  return (
    <AppBar position="static" color="primary" elevation={0}>
      <Toolbar>
        <Typography
          variant="h6"
          component={Link}
          to="/"
          sx={{
            textDecoration: 'none',
            color: 'inherit',
            display: 'flex',
            alignItems: 'center',
          }}
        >
          <HearingIcon sx={{ mr: 1 }} />
          한국어 듣기 연습
        </Typography>
        <Box sx={{ flexGrow: 1 }} />
        <Button
          color="inherit"
          component={Link}
          to="/videos"
          startIcon={<VideoLibraryIcon />}
        >
          비디오 목록
        </Button>
      </Toolbar>
    </AppBar>
  );
};

export default AppHeader;
