import React from 'react';
import { Snackbar, Alert } from '@mui/material';
import { useAppContext } from '../context/AppContext';

const NotificationManager = () => {
  const { state, actions } = useAppContext();
  const { notification } = state;

  const handleClose = () => {
    actions.clearNotification();
  };

  if (!notification) return null;

  return (
    <Snackbar
      open={Boolean(notification)}
      autoHideDuration={notification?.duration || 3000}
      onClose={handleClose}
      anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
    >
      <Alert 
        onClose={handleClose} 
        severity={notification.type || 'info'}
        variant="filled"
        sx={{ width: '100%' }}
      >
        {notification.message}
      </Alert>
    </Snackbar>
  );
};

export default NotificationManager;