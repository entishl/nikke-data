import axios from 'axios';

const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptors can be added here for handling things like authentication (tokens)
// or CSRF protection, as outlined in the project brief.
// For now, we'll keep it simple.

export default apiClient;
