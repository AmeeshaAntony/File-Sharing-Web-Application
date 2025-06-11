import React from 'react';
import { useNavigate, Link as RouterLink, useLocation } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';

function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, isAuthenticated, logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <AppBar position="static" sx={{ backgroundColor: '#F7F9FB', boxShadow: 'none' }}>
      <Toolbar>
        <Box sx={{ flexGrow: 1, display: 'flex', alignItems: 'center' }}>
          <Typography variant="h6" component="div" sx={{ color: '#333', fontWeight: 'bold' }}>
            File Sharing Application
          </Typography>
        </Box>

        {isAuthenticated && user ? (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Button 
              color="inherit" 
              component={RouterLink}
              to="/edit-profile"
              sx={{ color: '#0070e0', textTransform: 'none' }}
            >
              Edit Profile
            </Button>
            <Button 
              color="inherit" 
              component={RouterLink}
              to="/change-password"
              sx={{ color: '#0070e0', textTransform: 'none' }}
            >
              Change Password
            </Button>
            <Button 
              color="inherit" 
              onClick={handleLogout} 
              sx={{ color: '#0070e0', textTransform: 'none' }}
            >
              Logout
            </Button>
          </Box>
        ) : null}
      </Toolbar>
    </AppBar>
  );
}

export default Navbar; 