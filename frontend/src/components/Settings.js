import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemText,
  Switch,
  TextField,
  Button,
} from '@mui/material';
import axios from 'axios';

const Settings = () => {
  const [settings, setSettings] = useState({
    daily_goal: 2000,
    reminder_interval: 60,
    notifications_enabled: true,
  });

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await axios.get('http://localhost:5000/');
      setSettings(response.data.settings);
    } catch (error) {
      console.error('Error fetching settings:', error);
    }
  };

  const handleSave = async () => {
    try {
      const response = await axios.post(
        'http://localhost:5000/update_settings',
        settings
      );
      if (response.data.success) {
        alert('設置已保存！');
      }
    } catch (error) {
      console.error('Error saving settings:', error);
    }
  };

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h5" align="center" gutterBottom>
        設置
      </Typography>
      <List>
        <ListItem>
          <ListItemText primary="喝水提醒" />
          <Switch
            checked={settings.notifications_enabled}
            onChange={(e) =>
              setSettings({
                ...settings,
                notifications_enabled: e.target.checked,
              })
            }
            color="primary"
          />
        </ListItem>
        <ListItem>
          <ListItemText primary="提醒頻率（分鐘）" />
          <TextField
            type="number"
            value={settings.reminder_interval}
            onChange={(e) =>
              setSettings({
                ...settings,
                reminder_interval: parseInt(e.target.value),
              })
            }
            sx={{ width: 100 }}
          />
        </ListItem>
        <ListItem>
          <ListItemText primary="每日目標 (ml)" />
          <TextField
            type="number"
            value={settings.daily_goal}
            onChange={(e) =>
              setSettings({
                ...settings,
                daily_goal: parseInt(e.target.value),
              })
            }
            sx={{ width: 100 }}
          />
        </ListItem>
      </List>
      <Button
        variant="contained"
        fullWidth
        onClick={handleSave}
        sx={{ mt: 2 }}
      >
        保存設置
      </Button>
    </Box>
  );
};

export default Settings; 