import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Box,
  Alert
} from '@mui/material';
import axios from 'axios';

function ResetPassword() {
  const { token } = useParams();
  const navigate = useNavigate();
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    console.log('ResetPassword component mounted');
    console.log('Token from URL:', token);
  }, [token]);

  // Basic password validation (can enhance later)
  const validatePassword = (pwd) => {
    // Simple check: at least 8 characters
    return pwd.length >= 8;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess(false);

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (!validatePassword(password)) {
      setError('Password must be at least 8 characters long');
      return;
    }

    setLoading(true);

    try {
      console.log('Attempting to reset password with token:', token);
      const response = await axios.post(`http://localhost:5000/api/reset-password/${token}`, {
        password: password,
      });
      console.log('Password reset response:', response);
      setSuccess(true);
      setPassword('');
      setConfirmPassword('');
      // Optionally navigate to login after a delay
       setTimeout(() => {
         navigate('/login');
       }, 3000); // Navigate after 3 seconds

    } catch (err) {
      console.error('Error resetting password:', err);
      setError(err.response?.data?.error || 'An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 8 }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom align="center">
            Reset Password
          </Typography>
          
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          
          {success && (
            <Alert severity="success" sx={{ mb: 2 }}>
              Your password has been reset successfully! You will be redirected to the login page.
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <TextField
              margin="normal"
              required
              fullWidth
              label="New Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading || success}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              label="Confirm New Password"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              disabled={loading || success}
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={loading || success}
            >
              {loading ? 'Resetting...' : 'Reset Password'}
            </Button>
          </form>
        </Paper>
      </Box>
    </Container>
  );
}

export default ResetPassword; 