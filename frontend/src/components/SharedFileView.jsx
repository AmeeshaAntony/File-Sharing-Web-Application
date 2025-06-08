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
    const fetchFileDetails = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/api/shared/${token}`, {
          headers: {
            'Accept': 'application/json'
          }
        });
        setFileDetails(response.data);
      } catch (error) {
        console.error('Error fetching file details:', error);
        setError(error.response?.data?.error || 'Error loading file details');
      } finally {
        setLoading(false);
      }
    };

    fetchFileDetails();
  }, [token]);

  const handleDownload = () => {
    // Open the download URL in a new tab
    window.open(`http://localhost:5000/api/shared/${token}`, '_blank');
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
            Expires: {new Date(fileDetails?.expires_at).toLocaleString()}
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