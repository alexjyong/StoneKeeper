/**
 * API service for StoneKeeper frontend.
 *
 * Provides configured Axios instance for backend API communication
 * with automatic error handling and authentication.
 */
import axios, { AxiosInstance, AxiosError } from 'axios';

// API base URL (can be overridden by environment variable)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Configured Axios instance for API calls.
 *
 * Features:
 * - Automatic credential inclusion (for session cookies)
 * - Standardized error handling
 * - Request/response interceptors
 */
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,  // Include cookies for session authentication
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,  // 30 second timeout for most requests
});

/**
 * Request interceptor for adding authentication headers or logging.
 */
api.interceptors.request.use(
  (config) => {
    // Request logging for development
    if (import.meta.env.DEV) {
      console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    }
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

/**
 * Response interceptor for handling common errors.
 */
api.interceptors.response.use(
  (response) => {
    // Response logging for development
    if (import.meta.env.DEV) {
      console.log(`API Response: ${response.status} ${response.config.url}`);
    }
    return response;
  },
  (error: AxiosError) => {
    // Handle common error scenarios
    if (error.response) {
      // Server responded with error status
      const status = error.response.status;

      if (status === 401) {
        // Unauthorized - redirect to login
        console.warn('Unauthorized access - redirecting to login');
        // Redirect will be handled by components using this API
      } else if (status === 403) {
        console.error('Forbidden access');
      } else if (status === 404) {
        console.error('Resource not found');
      } else if (status >= 500) {
        console.error('Server error');
      }
    } else if (error.request) {
      // Request made but no response received
      console.error('No response from server - check network connection');
    } else {
      // Error setting up request
      console.error('Request setup error:', error.message);
    }

    return Promise.reject(error);
  }
);

export default api;

/**
 * Error response interface from backend.
 */
export interface ErrorResponse {
  error: string;
  message: string;
  details?: Record<string, any>;
}

/**
 * Paginated response interface from backend.
 */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

/**
 * Success response interface from backend.
 */
export interface SuccessResponse {
  success: boolean;
  message: string;
}

/**
 * Extract error message from API error response.
 */
export function getErrorMessage(error: any): string {
  if (error.response?.data?.message) {
    return error.response.data.message;
  } else if (error.message) {
    return error.message;
  } else {
    return 'An unexpected error occurred. Please try again.';
  }
}
