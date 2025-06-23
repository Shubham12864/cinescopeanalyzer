import API_CONFIG from '../config/api';

// Generic API call function
export const apiCall = async (endpoint, options = {}) => {
  const url = `${API_CONFIG.BASE_URL}${endpoint}`;
  
  const defaultOptions = {
    headers: API_CONFIG.DEFAULT_HEADERS,
    timeout: API_CONFIG.TIMEOUT,
  };

  const finalOptions = { ...defaultOptions, ...options };

  try {
    console.log(`Making API call to: ${url}`);
    
    const response = await fetch(url, finalOptions);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || `HTTP error! status: ${response.status}`);
    }

    console.log('API call successful:', data);
    return data;
  } catch (error) {
    console.error(`API call failed for ${endpoint}:`, error);
    throw error;
  }
};

// Health check function
export const checkBackendHealth = async () => {
  try {
    const response = await fetch('http://localhost:8000/health');
    const data = await response.json();
    return {
      isHealthy: response.ok,
      status: data.status || 'unknown'
    };
  } catch (error) {
    console.error('Backend health check failed:', error);
    return {
      isHealthy: false,
      status: 'error',
      error: error.message
    };
  }
};

// Error handler for API responses
export const handleApiError = (error) => {
  if (error.name === 'TypeError' && error.message.includes('fetch')) {
    return 'Backend server is not running. Please start the backend server.';
  }
  
  return error.message || 'An unexpected error occurred';
};