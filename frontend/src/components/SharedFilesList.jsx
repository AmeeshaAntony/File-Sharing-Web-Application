import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Tooltip,
  Button,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Download as DownloadIcon,
  Home as HomeIcon,
} from '@mui/icons-material';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function SharedFilesList() {
  const [sharedFiles, setSharedFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchSharedFiles();
  }, []);

  const fetchSharedFiles = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('Please login to view shared files');
        setLoading(false);
        return;
      }

      const response = await axios.get('http://localhost:5000/api/shared-files', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      setSharedFiles(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching shared files:', error);
      if (error.response?.status === 401) {
        setError('Your session has expired. Please login again.');
      } else {
        setError('Failed to load shared files. Please try again later.');
      }
      setLoading(false);
    }
  };

  const handleDownload = (shareToken) => {
    window.open(`http://localhost:5000/api/shared/${shareToken}`, '_blank');
  };

  if (loading) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
          <Typography>Loading shared files...</Typography>
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ mt: 4 }}>
          <Typography color="error">{error}</Typography>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Shared Files
        </Typography>
        {success && (
          <Typography color="success" sx={{ mb: 2 }}>
            {success}
          </Typography>
        )}
        {sharedFiles.length === 0 ? (
          <Typography>No files have been shared yet.</Typography>
        ) : (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>File Name</TableCell>
                  <TableCell>Share Date</TableCell>
                  <TableCell>Expires At</TableCell>
                  <TableCell>Recipient</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {sharedFiles.map((file) => (
                  <TableRow key={file.share_token}>
                    <TableCell>{file.filename}</TableCell>
                    <TableCell>{file.share_date}</TableCell>
                    <TableCell>{file.expires_at}</TableCell>
                    <TableCell>{file.recipient_email}</TableCell>
                    <TableCell>
                      {file.is_accessed ? (
                        <Chip
                          icon={<CheckCircleIcon />}
                          label="Accessed"
                          color="success"
                          size="small"
                        />
                      ) : (
                        <Chip
                          icon={<CancelIcon />}
                          label="Not Accessed"
                          color="default"
                          size="small"
                        />
                      )}
                    </TableCell>
                    <TableCell>
                      <Tooltip title="Download">
                        <IconButton
                          onClick={() => handleDownload(file.share_token)}
                          size="small"
                        >
                          <DownloadIcon />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
        <Box sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
          <Button
            variant="contained"
            startIcon={<HomeIcon />}
            onClick={() => navigate('/')}
            sx={{ minWidth: '200px' }}
          >
            Home
          </Button>
        </Box>
      </Box>
    </Container>
  );
}

export default SharedFilesList; 