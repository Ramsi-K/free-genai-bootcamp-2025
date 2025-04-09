import React from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';

const LoadingSpinner = ({ message = '로딩중...' }) => (
  <Box 
    sx={{ 
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '200px'
    }}
  >
    <CircularProgress size={40} />
    <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
      {message}
    </Typography>
  </Box>
);

export default LoadingSpinner;