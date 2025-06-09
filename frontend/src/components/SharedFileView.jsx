import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  Paper,
  CircularProgress,
} from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Download as DownloadIcon } from '@mui/icons-material';

function SharedFileView() {
  const { token } = useParams();
  const navigate = useNavigate();
  const [fileDetails, setFileDetails] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchFileDetails();
  }, [token]);

  const fetchFileDetails = async () => {
    try {
      console.log('Fetching file details for token:', token); // Debug log
      const response = await axios.get(`http://localhost:5000/api/shared/${token}`, {
        headers: {
          'Accept': 'application/json'
        }
      });
      console.log('File details response:', response.data); // Debug log
      setFileDetails(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching file details:', error);
      console.error('Error response:', error.response?.data); // Debug log
      
      if (error.response?.status === 404) {
        setError('Share link not found');
      } else if (error.response?.status === 410) {
        setError('Share link has expired');
      } else if (error.response?.status === 500) {
        const errorMessage = error.response?.data?.details || 'Server error. Please try again later.';
        setError(`Server error: ${errorMessage}`);
      } else {
        setError('Error loading file details. Please try again later.');
      }
      setLoading(false);
    }
  };

  const handleDownload = () => {
    try {
      // Create a temporary link element
      const link = document.createElement('a');
      link.href = `http://localhost:5000/api/shared/${token}`;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error('Error downloading file:', error);
      setError('Error downloading file. Please try again.');
    }
  };

  if (loading) {
    return (
      <Container maxWidth="sm">
        <Box sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="sm">
        <Box sx={{ mt: 4 }}>
          <Paper elevation={3} sx={{ p: 4, textAlign: 'center' }}>
            <Typography color="error" variant="h6" gutterBottom>
              {error}
            </Typography>
            <Button
              variant="contained"
              onClick={() => navigate('/')}
              sx={{ mt: 2 }}
            >
              Go to Home
            </Button>
          </Paper>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 4 }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Shared File
          </Typography>

          {fileDetails?.message && (
            <Typography variant="body1" sx={{ mb: 3 }}>
              Message: {fileDetails.message}
            </Typography>
          )}

          <Typography variant="h6" gutterBottom>
            {fileDetails?.filename}
          </Typography>

          <Typography variant="body2" color="text.secondary" gutterBottom>
            Size: {(fileDetails?.size / (1024 * 1024)).toFixed(2)} MB
          </Typography>

          <Typography variant="body2" color="text.secondary" gutterBottom>
            Expires: {fileDetails?.expires_at}
          </Typography>

          <Box sx={{ mt: 3 }}>
            <Button
              variant="contained"
              startIcon={<DownloadIcon />}
              onClick={handleDownload}
              fullWidth
            >
              Download File
            </Button>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
}

export default SharedFileView; 