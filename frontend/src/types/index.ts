/**
 * TypeScript type definitions for StoneKeeper frontend.
 *
 * Defines interfaces matching backend Pydantic schemas
 * for type-safe API communication.
 */

/**
 * User account information.
 */
export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
}

/**
 * User registration request.
 */
export interface UserRegister {
  email: string;
  password: string;
  full_name: string;
}

/**
 * User login request.
 */
export interface UserLogin {
  email: string;
  password: string;
}

/**
 * GPS coordinates.
 */
export interface GPSCoordinates {
  latitude: number;
  longitude: number;
}

/**
 * Cemetery information.
 */
export interface Cemetery {
  id: number;
  name: string;
  location_description?: string;
  gps_location?: GPSCoordinates;
  established_year?: number;
  notes?: string;
  created_by: number;
  created_at: string;
  updated_at: string;
}

/**
 * Cemetery creation request.
 */
export interface CemeteryCreate {
  name: string;
  location_description?: string;
  gps_location?: GPSCoordinates;
  established_year?: number;
  notes?: string;
}

/**
 * Cemetery section information.
 */
export interface Section {
  id: number;
  cemetery_id: number;
  name: string;
  description?: string;
  display_order: number;
  created_by: number;
  created_at: string;
  updated_at: string;
}

/**
 * Section creation request.
 */
export interface SectionCreate {
  name: string;
  description?: string;
  display_order?: number;
}

/**
 * Plot information.
 */
export interface Plot {
  id: number;
  section_id: number;
  plot_number?: string;
  row_identifier?: string;
  headstone_inscription?: string;
  burial_date?: string;
  notes?: string;
  created_by: number;
  created_at: string;
  updated_at: string;
}

/**
 * Plot creation request.
 */
export interface PlotCreate {
  plot_number?: string;
  row_identifier?: string;
  headstone_inscription?: string;
  burial_date?: string;
  notes?: string;
}

/**
 * EXIF metadata from photo.
 */
export interface EXIFMetadata {
  date_taken?: string;
  gps_location?: GPSCoordinates;
  camera_make?: string;
  camera_model?: string;
  focal_length?: string;
  aperture?: string;
  shutter_speed?: string;
  iso?: number;
  image_width?: number;
  image_height?: number;
}

/**
 * Photograph information.
 */
export interface Photograph {
  id: number;
  uuid: string;
  cemetery_id: number;
  section_id?: number;
  plot_id?: number;
  file_path: string;
  thumbnail_path?: string;
  preview_path?: string;
  file_size_bytes: number;
  file_format: string;
  exif_metadata?: EXIFMetadata;
  description?: string;
  photographer_notes?: string;
  uploaded_by: number;
  uploader_name?: string;
  created_at: string;
  updated_at: string;
}

/**
 * Photo upload request.
 */
export interface PhotoUpload {
  cemetery_id: number;
  section_id?: number;
  plot_id?: number;
  description?: string;
  photographer_notes?: string;
}

/**
 * Search filters.
 */
export interface SearchFilters {
  query?: string;
  cemetery_id?: number;
  section_id?: number;
  plot_id?: number;
  uploaded_by?: number;
  date_from?: string;
  date_to?: string;
  page?: number;
  page_size?: number;
}

/**
 * Error response from API.
 */
export interface ErrorResponse {
  error: string;
  message: string;
  details?: Record<string, any>;
}

/**
 * Success response from API.
 */
export interface SuccessResponse {
  success: boolean;
  message: string;
}

/**
 * Paginated response from API.
 */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
