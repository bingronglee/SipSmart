import React from 'react';
import { Paper, BottomNavigation, BottomNavigationAction } from '@mui/material';
import { Home, History, Settings } from '@mui/icons-material';

const Navigation = ({ currentScreen, onScreenChange }) => {
  return (
    <Paper
      sx={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        zIndex: 1000,
      }}
      elevation={3}
    >
      <BottomNavigation
        value={currentScreen}
        onChange={(event, newValue) => {
          onScreenChange(newValue);
        }}
        showLabels
      >
        <BottomNavigationAction
          label="首頁"
          value="dashboard"
          icon={<Home />}
        />
        <BottomNavigationAction
          label="歷史"
          value="history"
          icon={<History />}
        />
        <BottomNavigationAction
          label="設置"
          value="settings"
          icon={<Settings />}
        />
      </BottomNavigation>
    </Paper>
  );
};

export default Navigation; 