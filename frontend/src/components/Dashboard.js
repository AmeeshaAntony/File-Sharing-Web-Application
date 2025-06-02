import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Box,
} from '@mui/material';
import {
  Delete as DeleteIcon,
  Share as ShareIcon,
  CloudUpload as CloudUploadIcon,
} from '@mui/icons-material';
import axios from 'axios';

function Dashboard() {
  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [shareDialogOpen, setShareDialogOpen] = useState(false);
  const [shareUsername, setShareUsername] = useState('');
  const [selectedFileId, setSelectedFileId] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchFiles();
  }, []);

  const fetchFiles = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:5000/api/files', {
        headers: { Authorization: `Bearer ${token}` },
      });
      setFiles(response.data);
    } catch (error) {
      console.error('Error fetching files:', error);
    }
  };

  const handleFileSelect = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const token = localStorage.getItem('token');
      await axios.post('http://localhost:5000/api/upload', formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data',
        },
      });
      setSelectedFile(null);
      fetchFiles();
    } catch (error) {
      console.error('Error uploading file:', error);
      setError('Error uploading file');
    }
  };

  const handleDelete = async (fileId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`http://localhost:5000/api/files/${fileId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      fetchFiles();
    } catch (error) {
      console.error('Error deleting file:', error);
      setError('Error deleting file');
    }
  };

  const handleShare = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        'http://localhost:5000/api/share',
        {
          file_id: selectedFileId,
          username: shareUsername,
        },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      setShareDialogOpen(false);
      setShareUsername('');
      setSelectedFileId(null);
    } catch (error) {
      console.error('Error sharing file:', error);
      setError('Error sharing file');
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          My Files
        </Typography>
        {error && (
          <Typography color="error" gutterBottom>
            {error}
          </Typography>
        )}
        <Box sx={{ mb: 3 }}>
          <input
            type="file"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
            id="file-upload"
          />
          <label htmlFor="file-upload">
            <Button
              variant="contained"
              component="span"
              startIcon={<CloudUploadIcon />}
              sx={{ mr: 2 }}
            >
              Select File
            </Button>
          </label>
          {selectedFile && (
            <Button
              variant="contained"
              color="primary"
              onClick={handleUpload}
              sx={{ ml: 2 }}
            >
              Upload
            </Button>
          )}
        </Box>
        <List>
          {files.map((file) => (
            <ListItem key={file.id}>
              <ListItemText
                primary={file.filename}
                secondary={`Size: ${formatFileSize(file.size)} | Uploaded: ${new Date(
                  file.upload_date
                ).toLocaleString()}`}
              />
              <ListItemSecondaryAction>
                <IconButton
                  edge="end"
                  aria-label="share"
                  onClick={() => {
                    setSelectedFileId(file.id);
                    setShareDialogOpen(true);
                  }}
                  sx={{ mr: 1 }}
                >
                  <ShareIcon />
                </IconButton>
                <IconButton
                  edge="end"
                  aria-label="delete"
                  onClick={() => handleDelete(file.id)}
                >
                  <DeleteIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      </Paper>

      <Dialog open={shareDialogOpen} onClose={() => setShareDialogOpen(false)}>
        <DialogTitle>Share File</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Username"
            type="text"
            fullWidth
            value={shareUsername}
            onChange={(e) => setShareUsername(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShareDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleShare} color="primary">
            Share
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}

export default Dashboard; 