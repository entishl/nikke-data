import axios from 'axios';
import i18n from '@/plugins/i18n';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add the auth token
apiClient.interceptors.request.use(
  (config) => {
    console.log('API Interceptor: Reading token from localStorage:', localStorage.getItem('token'));
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    console.log('API Interceptor: Final headers being sent:', config.headers);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    let errorMessage = i18n.global.t('services.api.errors.network');
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error('API Error Response:', error.response.data);
      // Try to get a more specific message from the backend response
      const backendMessage = error.response.data.detail || error.response.data.message;
      errorMessage = backendMessage || `${i18n.global.t('services.api.errors.serverError')} ${error.response.status}`;
    } else if (error.request) {
      // The request was made but no response was received
      console.error('API No Response:', error.request);
      errorMessage = i18n.global.t('services.api.errors.noResponse');
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error('API Request Setup Error:', error.message);
      errorMessage = error.message;
    }
    // It's better to return a rejected promise with a user-friendly error message
    // The component/store can then decide how to display it (e.g., a toast notification)
    return Promise.reject(new Error(errorMessage));
  }
);

// Authentication specific API calls
export const login = (credentials) => {
  // FastAPI's OAuth2PasswordRequestForm expects form data
  const formData = new URLSearchParams();
  formData.append('username', credentials.username);
  formData.append('password', credentials.password);

  return apiClient.post('/api/auth/token', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
};

export const register = (userInfo) => {
  return apiClient.post('/api/users/', userInfo);
};


export default apiClient;
