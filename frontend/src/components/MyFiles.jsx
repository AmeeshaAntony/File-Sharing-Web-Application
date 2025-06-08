import React, { useState, useEffect, useCallback } from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Input,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Pagination,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Delete as DeleteIcon,
  Download as DownloadIcon,
  Share as ShareIcon,
  Description as FileIcon,
  AttachFile as AttachFileIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { Link as RouterLink } from 'react-router-dom';

const MAX_FILE_SIZE = 100 * 1024 * 1024; // 100 MB
const MAX_TOTAL_STORAGE = 1 * 1024 * 1024 * 1024; // 1 GB

function MyFiles() {
  const [files, setFiles] = useState([]);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [shareDialogOpen, setShareDialogOpen] = useState(false);
  const [selectedFileToShare, setSelectedFileToShare] = useState(null);
  const [shareEmail, setShareEmail] = useState('');
  const [dragOver, setDragOver] = useState(false);
  const [uploadError, setUploadError] = useState('');
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [fileToDeleteId, setFileToDeleteId] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const filesPerPage = 10;
  const { user, logout, isAuthenticated, accessToken } = useAuth();

  useEffect(() => {
    fetchFiles();
  }, [currentPage, searchTerm]);

  const fetchFiles = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/files', {
        params: {
          page: currentPage,
          per_page: filesPerPage,
          search: searchTerm,
        },
      });
      // Sort files by upload_date in descending order (latest first)
      const sortedFiles = response.data.files.sort((a, b) => new Date(b.upload_date) - new Date(a.upload_date));
      setFiles(sortedFiles);
      setTotalPages(Math.ceil(response.data.total_files / filesPerPage));
    } catch (error) {
      console.error('Error fetching files:', error);
    }
  };

  const handleFilesAdded = useCallback((newFiles) => {
    const validFiles = Array.from(newFiles).filter(file => {
      if (file.size > MAX_FILE_SIZE) {
        setUploadError('File size limit is 100mb');
        return false;
      }
      return true;
    });
    setSelectedFiles(prevFiles => [...prevFiles, ...validFiles]);
  }, []);

  const handleFileSelect = (event) => {
    handleFilesAdded(event.target.files);
  };

  const handleDragOver = useCallback((event) => {
    event.preventDefault();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setDragOver(false);
  }, []);

  const handleDrop = useCallback((event) => {
    event.preventDefault();
    setDragOver(false);
    handleFilesAdded(event.dataTransfer.files);
  }, [handleFilesAdded]);

  const handleRemoveSelectedFile = (fileToRemove) => {
    setSelectedFiles(prevFiles => prevFiles.filter(file => file !== fileToRemove));
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) return;

    const formData = new FormData();
    selectedFiles.forEach((file) => {
      formData.append('file', file);
    });

    try {
      console.log("Access Token for upload:", accessToken); // Debugging line
      await axios.post('http://localhost:5000/api/upload', formData, {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
      });
      setUploadDialogOpen(false);
      setSelectedFiles([]);
      setUploadError('');
      fetchFiles();
    } catch (error) {
      console.error('Error uploading file:', error);
      setUploadError('Error uploading files.');
      if (error.response && error.response.status === 401) {
        logout();
      }
    }
  };

  const confirmDelete = (fileId) => {
    setFileToDeleteId(fileId);
    setDeleteConfirmOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (fileToDeleteId) {
      try {
        await axios.delete(`http://localhost:5000/api/files/${fileToDeleteId}`);
        fetchFiles();
      } catch (error) {
        console.error('Error deleting file:', error);
      }
    }
    setDeleteConfirmOpen(false);
    setFileToDeleteId(null);
  };

  const handleCloseDeleteConfirm = () => {
    setDeleteConfirmOpen(false);
    setFileToDeleteId(null);
  };

  const handleDownload = async (fileId, filename) => {
    try {
      const response = await axios.get(`http://localhost:5000/api/files/${fileId}/download`, {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error downloading file:', error);
    }
  };

  const handleShare = async () => {
    if (!selectedFileToShare || !shareEmail) return;

    try {
      await axios.post(`http://localhost:5000/api/files/${selectedFileToShare.id}/share`, {
        email: shareEmail,
      });
      setShareDialogOpen(false);
      setSelectedFileToShare(null);
      setShareEmail('');
    } catch (error) {
      console.error('Error sharing file:', error);
    }
  };

  const handlePageChange = (event, value) => {
    setCurrentPage(value);
  };

  const debouncedSearch = useCallback(
    debounce((value) => {
      setSearchTerm(value);
      setCurrentPage(1);
    }, 500),
    []
  );

  const handleSearchChange = (event) => {
    debouncedSearch(event.target.value);
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Welcome, {user?.first_name}!
        </Typography>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="contained"
              startIcon={<UploadIcon />}
              onClick={() => setUploadDialogOpen(true)}
            >
              Upload File
            </Button>
            <Button
              variant="outlined"
              component={RouterLink}
              to="/"
            >
              Home Page
            </Button>
          </Box>
          <TextField
            label="Search files"
            variant="outlined"
            size="small"
            onChange={handleSearchChange}
          />
        </Box>

        <Grid container spacing={3}>
          {files.length === 0 ? (
            <Typography variant="h6" sx={{ mt: 4, width: '100%', textAlign: 'center' }}>
              No files uploaded yet.
            </Typography>
          ) : (
            files.map((file) => (
              <Grid item xs={12} sm={6} md={4} key={file.id}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" component="div">
                      {file.filename}
                    </Typography>
                    <Typography color="text.secondary">
                      Uploaded: {new Date(file.upload_date).toLocaleDateString()}
                    </Typography>
                  </CardContent>
                  <CardActions>
                    <IconButton
                      onClick={() => handleDownload(file.id, file.filename)}
                      color="primary"
                    >
                      <DownloadIcon />
                    </IconButton>
                    <IconButton
                      onClick={() => {
                        setSelectedFileToShare(file);
                        setShareDialogOpen(true);
                      }}
                      color="primary"
                    >
                      <ShareIcon />
                    </IconButton>
                    <IconButton
                      onClick={() => confirmDelete(file.id)}
                      color="error"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </CardActions>
                </Card>
              </Grid>
            ))
          )}
        </Grid>

        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <Pagination
            count={totalPages}
            page={currentPage}
            onChange={handlePageChange}
            color="primary"
          />
        </Box>

        {/* Upload Dialog */}
        <Dialog open={uploadDialogOpen} onClose={() => setUploadDialogOpen(false)}>
          <DialogTitle>Upload File</DialogTitle>
          <DialogContent dividers>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Max individual file size: {MAX_FILE_SIZE / (1024 * 1024)} MB. Total storage per user: {MAX_TOTAL_STORAGE / (1024 * 1024 * 1024)} GB.
            </Typography>
            <Box
              sx={{
                border: '2px dashed #ccc',
                borderRadius: 2,
                p: 4,
                textAlign: 'center',
                cursor: 'pointer',
                backgroundColor: dragOver ? '#e0e0e0' : 'transparent',
                transition: 'background-color 0.3s ease',
              }}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <input
                accept="*/*"
                style={{ display: 'none' }}
                id="file-upload"
                multiple
                type="file"
                onChange={handleFileSelect}
              />
              <label htmlFor="file-upload">
                <Button variant="contained" component="span" startIcon={<AttachFileIcon />}>
                  Select Files
                </Button>
              </label>
              <Typography variant="body1" sx={{ mt: 2 }}>
                or Drag and Drop files here
              </Typography>
            </Box>
            {selectedFiles.length > 0 && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle1">Selected Files:</Typography>
                <List>
                  {selectedFiles.map((file, index) => (
                    <ListItem key={index} secondaryAction={
                      <IconButton edge="end" aria-label="delete" onClick={() => handleRemoveSelectedFile(file)}>
                        <CloseIcon />
                      </IconButton>
                    }>
                      <ListItemIcon>
                        <FileIcon />
                      </ListItemIcon>
                      <ListItemText primary={file.name} secondary={`${(file.size / (1024 * 1024)).toFixed(2)} MB`} />
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}
            {uploadError && (
              <Typography color="error" sx={{ mt: 2 }}>
                {uploadError}
              </Typography>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => {
              setUploadDialogOpen(false);
              setSelectedFiles([]);
              setUploadError('');
            }}>Cancel</Button>
            <Button onClick={handleUpload} variant="contained" disabled={selectedFiles.length === 0}>
              Upload
            </Button>
          </DialogActions>
        </Dialog>

        {/* Delete Confirmation Dialog */}
        <Dialog
          open={deleteConfirmOpen}
          onClose={handleCloseDeleteConfirm}
          aria-labelledby="alert-dialog-title"
          aria-describedby="alert-dialog-description"
        >
          <DialogTitle id="alert-dialog-title">
            {"Confirm Deletion"}
          </DialogTitle>
          <DialogContent>
            <Typography id="alert-dialog-description">
              Are you sure you want to delete this file?
            </Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDeleteConfirm}>No</Button>
            <Button onClick={handleConfirmDelete} autoFocus>
              Yes
            </Button>
          </DialogActions>
        </Dialog>

        {/* Share Dialog */}
        <Dialog open={shareDialogOpen} onClose={() => setShareDialogOpen(false)}>
          <DialogTitle>Share File</DialogTitle>
          <DialogContent>
            <TextField
              autoFocus
              margin="dense"
              label="Email Address"
              type="email"
              fullWidth
              value={shareEmail}
              onChange={(e) => setShareEmail(e.target.value)}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setShareDialogOpen(false)}>Cancel</Button>
            <Button onClick={handleShare} variant="contained">
              Share
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Container>
  );
}

export default MyFiles;

const debounce = (func, delay) => {
  let timeout;
  return function(...args) {
    const context = this;
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(context, args), delay);
  };
}; 