import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Button,
  TextField,
  CircularProgress,
} from '@mui/material';
import { LocalDrink } from '@mui/icons-material';
import axios from 'axios';

const Dashboard = () => {
  const [waterData, setWaterData] = useState({
    total: 0,
    goal: 2000,
    percentage: 0,
  });
  const [customAmount, setCustomAmount] = useState('');

  useEffect(() => {
    // 獲取今日喝水數據
    fetchWaterData();
  }, []);

  const fetchWaterData = async () => {
    try {
      const response = await axios.get('http://localhost:5000/');
      setWaterData({
        total: response.data.total_today,
        goal: response.data.goal,
        percentage: response.data.percentage,
      });
    } catch (error) {
      console.error('Error fetching water data:', error);
    }
  };

  const logWater = async (amount) => {
    try {
      const response = await axios.post('http://localhost:5000/log_water', {
        amount,
      });
      if (response.data.success) {
        setWaterData({
          ...waterData,
          total: response.data.total,
          percentage: response.data.percentage,
        });
        setCustomAmount('');
      }
    } catch (error) {
      console.error('Error logging water:', error);
    }
  };

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h5" align="center" gutterBottom>
        今日喝水目標
      </Typography>

      <Box
        sx={{
          position: 'relative',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          my: 4,
        }}
      >
        <CircularProgress
          variant="determinate"
          value={waterData.percentage}
          size={200}
          thickness={4}
          sx={{
            color: 'primary.main',
            backgroundColor: 'secondary.main',
            borderRadius: '50%',
          }}
        />
        <Box
          sx={{
            position: 'absolute',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
          }}
        >
          <Typography variant="h4" color="primary">
            {waterData.percentage}%
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {waterData.total}ml / {waterData.goal}ml
          </Typography>
        </Box>
      </Box>

      <Grid container spacing={2} sx={{ mb: 3 }}>
        {[250, 500, 750].map((amount) => (
          <Grid item xs={4} key={amount}>
            <Button
              variant="outlined"
              fullWidth
              onClick={() => logWater(amount)}
              startIcon={<LocalDrink />}
              sx={{
                borderColor: 'primary.main',
                color: 'primary.main',
                '&:hover': {
                  backgroundColor: 'primary.main',
                  color: 'white',
                },
              }}
            >
              {amount}ml
            </Button>
          </Grid>
        ))}
      </Grid>

      <Box sx={{ mt: 2 }}>
        <Typography variant="subtitle1" gutterBottom>
          自訂喝水量 (ml)
        </Typography>
        <TextField
          fullWidth
          type="number"
          value={customAmount}
          onChange={(e) => setCustomAmount(e.target.value)}
          placeholder="請輸入毫升數"
          sx={{ mb: 2 }}
        />
        <Button
          variant="contained"
          fullWidth
          onClick={() => {
            if (customAmount) {
              logWater(parseInt(customAmount));
            }
          }}
          disabled={!customAmount}
        >
          確認添加
        </Button>
      </Box>
    </Box>
  );
};

export default Dashboard; 