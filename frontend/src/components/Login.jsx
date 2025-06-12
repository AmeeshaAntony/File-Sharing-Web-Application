import React, { useState } from 'react';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Link,
  Box,
  Grid,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { login } = useAuth();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const success = await login(email, password);
      if (success) {
        navigate('/');
      }
    } catch (err) {
      setError(err.message || 'An error occurred during login');
    }
  };

  return (
    <Container 
      maxWidth="sm" 
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        py: { xs: 2, sm: 4, md: 6 },
        px: { xs: 2, sm: 3, md: 4 }
      }}
    >
      <Paper 
        elevation={3} 
        sx={{ 
          p: { xs: 2, sm: 3, md: 4 },
          width: '100%',
          maxWidth: '450px',
          mx: 'auto'
        }}
      >
        <Typography 
          variant="h4" 
          component="h1" 
          gutterBottom 
          align="center"
          sx={{
            fontSize: { xs: '1.75rem', sm: '2rem', md: '2.125rem' },
            fontWeight: 'bold',
            mb: 3
          }}
        >
          Login
        </Typography>
        {error && (
          <Typography 
            color="error" 
            align="center" 
            gutterBottom
            sx={{ mb: 2 }}
          >
            {error}
          </Typography>
        )}
        <form onSubmit={handleSubmit}>
          <TextField
            margin="normal"
            required
            fullWidth
            label="Email Address"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            sx={{
              mb: { xs: 1.5, sm: 2 },
              '& .MuiOutlinedInput-root': {
                fontSize: { xs: '0.875rem', sm: '1rem' }
              }
            }}
          />
          <TextField
            margin="normal"
            required
            fullWidth
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            sx={{
              mb: { xs: 1.5, sm: 2 },
              '& .MuiOutlinedInput-root': {
                fontSize: { xs: '0.875rem', sm: '1rem' }
              }
            }}
          />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ 
              mt: { xs: 2, sm: 3 },
              mb: { xs: 2, sm: 3 },
              py: { xs: 1, sm: 1.5 },
              fontSize: { xs: '0.875rem', sm: '1rem' }
            }}
          >
            Login
          </Button>
          <Grid 
            container 
            spacing={2}
            sx={{
              mt: { xs: 1, sm: 2 },
              flexDirection: { xs: 'column', sm: 'row' },
              alignItems: { xs: 'center', sm: 'flex-start' }
            }}
          >
            <Grid item xs={12} sm={6}>
              <Link 
                component={RouterLink} 
                to="/register" 
                variant="body2"
                sx={{
                  display: 'block',
                  textAlign: { xs: 'center', sm: 'left' },
                  fontSize: { xs: '0.875rem', sm: '0.875rem' }
                }}
              >
                Don't have an account? Sign up
              </Link>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Link 
                component={RouterLink} 
                to="/forgot-password" 
                variant="body2"
                sx={{
                  display: 'block',
                  textAlign: { xs: 'center', sm: 'right' },
                  fontSize: { xs: '0.875rem', sm: '0.875rem' }
                }}
              >
                Forgot Password?
              </Link>
            </Grid>
          </Grid>
        </form>
      </Paper>
    </Container>
  );
}

export default Login; 