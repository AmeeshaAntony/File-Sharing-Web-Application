import React from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  Avatar,
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

function Dashboard() {
  const { user } = useAuth();

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: 'calc(100vh - 64px)', // Adjust based on Navbar height
        backgroundColor: '#D1EEFF', // Light blue background color
        textAlign: 'center',
        padding: 4,
        backgroundImage: 'url("https://www.dropbox.com/static/images/empty_states/thumb_mac_and_hands.png")', // Placeholder image, replace with actual
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
      }}
    >
      {user && (
        <Box sx={{ mb: 3, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <Avatar
            src={user.profile_photo ? `http://localhost:5000/profile_photos/${user.profile_photo}` : ''}
            sx={{ width: 100, height: 100, mb: 2 }}
          />
          <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold', color: '#333' }}>
            Welcome, {user.first_name} {user.last_name}!
          </Typography>
        </Box>
      )}

      <Typography variant="h3" component="h1" gutterBottom sx={{ fontWeight: 'bold', color: '#333' }}>
      Sharing made simple—just upload, 
        <br />
        share, and relax.
      </Typography>
      <Typography variant="h6" component="p" sx={{ mb: 4, color: '#555' }}>
      Seamlessly share your files—anytime, anywhere, with anyone.
        <br />
        Secure. Simple. Swift.
      </Typography>
      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
        <Button
          variant="contained"
          component={RouterLink}
          to="/my-files"
          sx={{
            backgroundColor: '#0070e0',
            '&:hover': {
              backgroundColor: '#005bb5',
            },
            color: 'white',
            padding: '12px 24px',
            fontSize: '1rem',
          }}
        >
          My Files
        </Button>
        <Button
          variant="outlined"
          component={RouterLink}
          to="/shared-files"
          sx={{
            borderColor: '#0070e0',
            color: '#0070e0',
            padding: '12px 24px',
            fontSize: '1rem',
            '&:hover': {
              backgroundColor: 'rgba(0, 112, 224, 0.04)',
            },
          }}
        >
          Shared Files
        </Button>
      </Box>
      <Typography variant="body2" sx={{ color: '#777' }}>

      </Typography>
    </Box>
  );
}

export default Dashboard; 