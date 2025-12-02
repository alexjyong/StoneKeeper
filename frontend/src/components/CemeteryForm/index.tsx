/**
 * CemeteryForm component for StoneKeeper.
 *
 * Form for creating/editing cemetery records with GPS validation.
 */
import React, { useState } from 'react';
import type { CemeteryCreate, GPSCoordinates } from '../../types';
import './styles.css';

interface CemeteryFormProps {
  onSubmit: (cemetery: CemeteryCreate) => Promise<void>;
  onCancel?: () => void;
  initialData?: Partial<CemeteryCreate>;
  submitLabel?: string;
}

/**
 * Cemetery form component with GPS coordinate validation.
 *
 * Per Constitution Principle II: User-friendly for non-technical researchers.
 * Provides clear labels, validation messages, and optional fields.
 */
const CemeteryForm: React.FC<CemeteryFormProps> = ({
  onSubmit,
  onCancel,
  initialData,
  submitLabel = 'Create Cemetery'
}) => {
  const [formData, setFormData] = useState<CemeteryCreate>({
    name: initialData?.name || '',
    location_description: initialData?.location_description || '',
    gps_location: initialData?.gps_location || undefined,
    established_year: initialData?.established_year || undefined,
    notes: initialData?.notes || ''
  });

  const [gpsInput, setGpsInput] = useState({
    latitude: initialData?.gps_location?.latitude?.toString() || '',
    longitude: initialData?.gps_location?.longitude?.toString() || ''
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  /**
   * Validate GPS coordinates.
   * Latitude: -90 to 90
   * Longitude: -180 to 180
   */
  const validateGPS = (lat: string, lon: string): { valid: boolean; errors: string[] } => {
    const errors: string[] = [];

    if (lat && lon) {
      const latNum = parseFloat(lat);
      const lonNum = parseFloat(lon);

      if (isNaN(latNum)) {
        errors.push('Latitude must be a number');
      } else if (latNum < -90 || latNum > 90) {
        errors.push('Latitude must be between -90 and 90');
      }

      if (isNaN(lonNum)) {
        errors.push('Longitude must be a number');
      } else if (lonNum < -180 || lonNum > 180) {
        errors.push('Longitude must be between -180 and 180');
      }
    } else if (lat || lon) {
      errors.push('Both latitude and longitude are required for GPS coordinates');
    }

    return { valid: errors.length === 0, errors };
  };

  /**
   * Handle form field changes.
   */
  const handleChange = (field: keyof CemeteryCreate, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error for this field
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  /**
   * Handle GPS input changes.
   */
  const handleGPSChange = (field: 'latitude' | 'longitude', value: string) => {
    setGpsInput(prev => ({ ...prev, [field]: value }));
    // Clear GPS errors
    if (errors.gps_location) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors.gps_location;
        return newErrors;
      });
    }
  };

  /**
   * Validate and submit form.
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const newErrors: Record<string, string> = {};

    // Validate required fields
    if (!formData.name.trim()) {
      newErrors.name = 'Cemetery name is required';
    }

    // Validate GPS if provided
    if (gpsInput.latitude || gpsInput.longitude) {
      const gpsValidation = validateGPS(gpsInput.latitude, gpsInput.longitude);
      if (!gpsValidation.valid) {
        newErrors.gps_location = gpsValidation.errors.join('. ');
      }
    }

    // Validate year if provided
    if (formData.established_year) {
      const year = formData.established_year;
      const currentYear = new Date().getFullYear();
      if (year < 1500 || year > currentYear) {
        newErrors.established_year = `Year must be between 1500 and ${currentYear}`;
      }
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    // Build GPS coordinates if provided
    let gpsLocation: GPSCoordinates | undefined = undefined;
    if (gpsInput.latitude && gpsInput.longitude) {
      gpsLocation = {
        latitude: parseFloat(gpsInput.latitude),
        longitude: parseFloat(gpsInput.longitude)
      };
    }

    // Submit form
    setIsSubmitting(true);
    try {
      await onSubmit({
        ...formData,
        gps_location: gpsLocation
      });
    } catch (error) {
      console.error('Form submission error:', error);
      setErrors({ submit: 'Failed to save cemetery. Please try again.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form className="cemetery-form" onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor="name" className="required">Cemetery Name</label>
        <input
          id="name"
          type="text"
          value={formData.name}
          onChange={(e) => handleChange('name', e.target.value)}
          placeholder="e.g., Green Hills Cemetery"
          maxLength={255}
          disabled={isSubmitting}
          className={errors.name ? 'error' : ''}
        />
        {errors.name && <span className="error-message">{errors.name}</span>}
      </div>

      <div className="form-group">
        <label htmlFor="location_description">Location Description</label>
        <textarea
          id="location_description"
          value={formData.location_description || ''}
          onChange={(e) => handleChange('location_description', e.target.value)}
          placeholder="e.g., 123 Main Street, Springfield, IL 62701 (optional)"
          rows={3}
          disabled={isSubmitting}
        />
        <span className="help-text">Address or directions to the cemetery</span>
      </div>

      <div className="form-group">
        <label>GPS Coordinates (optional)</label>
        <div className="gps-inputs">
          <div className="gps-input">
            <label htmlFor="latitude">Latitude</label>
            <input
              id="latitude"
              type="text"
              value={gpsInput.latitude}
              onChange={(e) => handleGPSChange('latitude', e.target.value)}
              placeholder="e.g., 39.7817"
              disabled={isSubmitting}
              className={errors.gps_location ? 'error' : ''}
            />
            <span className="help-text">-90 to 90</span>
          </div>
          <div className="gps-input">
            <label htmlFor="longitude">Longitude</label>
            <input
              id="longitude"
              type="text"
              value={gpsInput.longitude}
              onChange={(e) => handleGPSChange('longitude', e.target.value)}
              placeholder="e.g., -89.6501"
              disabled={isSubmitting}
              className={errors.gps_location ? 'error' : ''}
            />
            <span className="help-text">-180 to 180</span>
          </div>
        </div>
        {errors.gps_location && <span className="error-message">{errors.gps_location}</span>}
        <span className="help-text">GPS coordinates for mapping (leave blank if unknown)</span>
      </div>

      <div className="form-group">
        <label htmlFor="established_year">Established Year (optional)</label>
        <input
          id="established_year"
          type="number"
          value={formData.established_year || ''}
          onChange={(e) => handleChange('established_year', e.target.value ? parseInt(e.target.value) : undefined)}
          placeholder="e.g., 1855"
          min={1500}
          max={new Date().getFullYear()}
          disabled={isSubmitting}
          className={errors.established_year ? 'error' : ''}
        />
        {errors.established_year && <span className="error-message">{errors.established_year}</span>}
      </div>

      <div className="form-group">
        <label htmlFor="notes">Notes (optional)</label>
        <textarea
          id="notes"
          value={formData.notes || ''}
          onChange={(e) => handleChange('notes', e.target.value)}
          placeholder="Historical information, access notes, etc."
          rows={4}
          disabled={isSubmitting}
        />
      </div>

      {errors.submit && (
        <div className="error-message submit-error">{errors.submit}</div>
      )}

      <div className="form-actions">
        {onCancel && (
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onCancel}
            disabled={isSubmitting}
          >
            Cancel
          </button>
        )}
        <button
          type="submit"
          className="btn btn-primary"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Saving...' : submitLabel}
        </button>
      </div>
    </form>
  );
};

export default CemeteryForm;
