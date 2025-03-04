import React, { useState } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Container, Box } from '@mui/material';
import Dashboard from './components/Dashboard';
import History from './components/History';
import Settings from './components/Settings';
import Navigation from './components/Navigation';

const theme = createTheme({
  palette: {
    primary: {
      main: '#80deea',
    },
    secondary: {
      main: '#e0f7fa',
    },
    background: {
      default: '#f7f7f7',
    },
  },
  typography: {
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  },
});

function App() {
  const [currentScreen, setCurrentScreen] = useState('dashboard');

  const renderScreen = () => {
    switch (currentScreen) {
      case 'dashboard':
        return <Dashboard />;
      case 'history':
        return <History />;
      case 'settings':
        return <Settings />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="sm">
        <Box
          sx={{
            minHeight: '100vh',
            display: 'flex',
            flexDirection: 'column',
            pt: 2,
            pb: 7,
          }}
        >
          {renderScreen()}
          <Navigation
            currentScreen={currentScreen}
            onScreenChange={setCurrentScreen}
          />
        </Box>
      </Container>
    </ThemeProvider>
  );
}

export default App; 