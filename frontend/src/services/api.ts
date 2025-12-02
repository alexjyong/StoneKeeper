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

// =============================================================================
// Cemetery API Methods
// =============================================================================

import type { Cemetery, CemeteryCreate, Photograph, PhotoUpload, SearchFilters } from '../types';

/**
 * Create a new cemetery.
 */
export async function createCemetery(cemetery: CemeteryCreate): Promise<Cemetery> {
  const response = await api.post<Cemetery>('/api/cemeteries/', cemetery);
  return response.data;
}

/**
 * Get list of cemeteries with optional search.
 */
export async function getCemeteries(
  page: number = 1,
  page_size: number = 20,
  search?: string
): Promise<PaginatedResponse<Cemetery>> {
  const response = await api.get<PaginatedResponse<Cemetery>>('/api/cemeteries/', {
    params: { page, page_size, search }
  });
  return response.data;
}

/**
 * Get cemetery by ID.
 */
export async function getCemetery(id: number): Promise<Cemetery> {
  const response = await api.get<Cemetery>(`/api/cemeteries/${id}`);
  return response.data;
}

/**
 * Update a cemetery.
 */
export async function updateCemetery(id: number, cemetery: Partial<CemeteryCreate>): Promise<Cemetery> {
  const response = await api.patch<Cemetery>(`/api/cemeteries/${id}`, cemetery);
  return response.data;
}

/**
 * Delete a cemetery (soft delete).
 */
export async function deleteCemetery(id: number): Promise<SuccessResponse> {
  const response = await api.delete<SuccessResponse>(`/api/cemeteries/${id}`);
  return response.data;
}

// =============================================================================
// Photo API Methods
// =============================================================================

/**
 * Upload a photo with metadata.
 *
 * @param file - Image file to upload
 * @param metadata - Photo metadata (cemetery_id required)
 * @param onProgress - Optional progress callback (0-100)
 */
export async function uploadPhoto(
  file: File,
  metadata: PhotoUpload,
  onProgress?: (progress: number) => void
): Promise<Photograph> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('cemetery_id', metadata.cemetery_id.toString());

  if (metadata.section_id) {
    formData.append('section_id', metadata.section_id.toString());
  }
  if (metadata.plot_id) {
    formData.append('plot_id', metadata.plot_id.toString());
  }
  if (metadata.description) {
    formData.append('description', metadata.description);
  }
  if (metadata.photographer_notes) {
    formData.append('photographer_notes', metadata.photographer_notes);
  }

  const response = await api.post<Photograph>('/api/photos/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    timeout: 120000,  // 2 minute timeout for uploads
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const percentComplete = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(percentComplete);
      }
    },
  });

  return response.data;
}

/**
 * Get photo metadata by ID.
 */
export async function getPhoto(id: number): Promise<Photograph> {
  const response = await api.get<Photograph>(`/api/photos/${id}`);
  return response.data;
}

/**
 * Get list of photos with filters.
 */
export async function getPhotos(filters: SearchFilters): Promise<PaginatedResponse<Photograph>> {
  const response = await api.get<PaginatedResponse<Photograph>>('/api/photos/', {
    params: filters
  });
  return response.data;
}

/**
 * Get URL for photo file (original).
 */
export function getPhotoFileUrl(id: number): string {
  return `${API_BASE_URL}/api/photos/${id}/file`;
}

/**
 * Get URL for photo thumbnail.
 */
export function getPhotoThumbnailUrl(id: number): string {
  return `${API_BASE_URL}/api/photos/${id}/thumbnail`;
}

/**
 * Get URL for photo preview.
 */
export function getPhotoPreviewUrl(id: number): string {
  return `${API_BASE_URL}/api/photos/${id}/preview`;
}
