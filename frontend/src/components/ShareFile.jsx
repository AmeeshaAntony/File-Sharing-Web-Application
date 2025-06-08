import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  TextField,
  Button,
  MenuItem,
  Paper,
} from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

function ShareFile() {
  const { fileId } = useParams();
  const navigate = useNavigate();
  const { accessToken } = useAuth();
  const [fileDetails, setFileDetails] = useState(null);
  const [formData, setFormData] = useState({
    email: '',
    expiration_time: '24', // Default 24 hours
    message: '',
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    const fetchFileDetails = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/api/files/${fileId}`, {
          headers: {
            'Authorization': `Bearer ${accessToken}`,
          },
        });
        setFileDetails(response.data);
      } catch (error) {
        console.error('Error fetching file details:', error);
        setError('Error loading file details');
      }
    };

    fetchFileDetails();
  }, [fileId, accessToken]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      await axios.post('http://localhost:5000/api/share', {
        file_id: fileId,
        email: formData.email,
        expiration_time: parseInt(formData.expiration_time),
        message: formData.message,
      }, {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
      });

      setSuccess('File shared successfully!');
      setTimeout(() => {
        navigate('/my-files');
      }, 2000);
    } catch (error) {
      console.error('Error sharing file:', error);
      setError(error.response?.data?.error || 'Error sharing file');
    }
  };

  if (!fileDetails) {
    return <Typography>Loading...</Typography>;
  }

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 4 }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Share File: {fileDetails.filename}
          </Typography>

          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Recipient Email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              required
              margin="normal"
            />

            <TextField
              fullWidth
              select
              label="Expiration Time"
              name="expiration_time"
              value={formData.expiration_time}
              onChange={handleChange}
              required
              margin="normal"
            >
              <MenuItem value="1">1 hour</MenuItem>
              <MenuItem value="24">24 hours</MenuItem>
              <MenuItem value="72">3 days</MenuItem>
              <MenuItem value="168">7 days</MenuItem>
              <MenuItem value="720">30 days</MenuItem>
            </TextField>

            <TextField
              fullWidth
              label="Message"
              name="message"
              value={formData.message}
              onChange={handleChange}
              multiline
              rows={4}
              margin="normal"
              placeholder="Add a message to include with the share link..."
            />

            {error && (
              <Typography color="error" sx={{ mt: 2 }}>
                {error}
              </Typography>
            )}

            {success && (
              <Typography color="success.main" sx={{ mt: 2 }}>
                {success}
              </Typography>
            )}

            <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
              <Button
                variant="outlined"
                onClick={() => navigate('/my-files')}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="contained"
                color="primary"
              >
                Share File
              </Button>
            </Box>
          </form>
        </Paper>
      </Box>
    </Container>
  );
}

export default ShareFile; 