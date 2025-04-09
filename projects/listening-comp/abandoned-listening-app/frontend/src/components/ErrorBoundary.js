import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <Box sx={{ 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'center', 
          justifyContent: 'center',
          minHeight: '50vh',
          p: 3,
          textAlign: 'center'
        }}>
          <Typography variant="h4" gutterBottom color="error">
            오류가 발생했습니다
          </Typography>
          <Typography variant="body1" color="text.secondary" paragraph>
            죄송합니다. 예상치 못한 오류가 발생했습니다. 
            다시 시도하거나 지원팀에 문의해주세요.
          </Typography>
          <Button 
            variant="contained" 
            onClick={() => window.location.href = '/'}
            sx={{ mt: 2 }}
          >
            홈으로 돌아가기
          </Button>
        </Box>
      );
    }

    return this.props.children;
  }
}


export default ErrorBoundary;