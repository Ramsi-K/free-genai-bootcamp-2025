import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { AppProvider } from './context/AppContext';
import ErrorBoundary from './components/ErrorBoundary';
import NotificationManager from './components/NotificationManager';
import AppRoutes from './routes';
import theme from './theme';
import AppHeader from './components/AppHeader';
import Footer from './components/Footer';

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <AppProvider>
          <BrowserRouter>
            <div style={{ 
              display: 'flex', 
              flexDirection: 'column', 
              minHeight: '100vh' 
            }}>
              <NotificationManager />
              <AppHeader />
              <main style={{ flexGrow: 1, padding: '20px' }}>
                <AppRoutes />
              </main>
              <Footer />
            </div>
          </BrowserRouter>
        </AppProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
