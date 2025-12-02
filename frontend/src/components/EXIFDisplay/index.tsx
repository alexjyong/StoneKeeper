/**
 * EXIFDisplay component for StoneKeeper.
 *
 * Displays extracted EXIF metadata in a readable format.
 */
import React from 'react';
import type { EXIFMetadata } from '../../types';
import './styles.css';

interface EXIFDisplayProps {
  exif: EXIFMetadata;
}

/**
 * Format date for display.
 */
const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

/**
 * Format GPS coordinates for display.
 */
const formatGPS = (lat: number, lon: number): string => {
  const latDir = lat >= 0 ? 'N' : 'S';
  const lonDir = lon >= 0 ? 'E' : 'W';
  return `${Math.abs(lat).toFixed(6)}° ${latDir}, ${Math.abs(lon).toFixed(6)}° ${lonDir}`;
};

/**
 * EXIF metadata display component.
 *
 * Shows extracted metadata in user-friendly format per
 * Constitution Principle II: Non-Technical User Focus.
 */
const EXIFDisplay: React.FC<EXIFDisplayProps> = ({ exif }) => {
  const hasAnyData = Object.values(exif).some(value => value !== undefined && value !== null);

  if (!hasAnyData) {
    return (
      <div className="exif-display empty">
        <p className="no-data">No EXIF metadata available for this photo.</p>
      </div>
    );
  }

  return (
    <div className="exif-display">
      <h3 className="exif-title">Photo Information</h3>

      <div className="exif-grid">
        {/* Date Taken */}
        {exif.date_taken && (
          <div className="exif-item">
            <span className="exif-label">Date Taken</span>
            <span className="exif-value">{formatDate(exif.date_taken)}</span>
          </div>
        )}

        {/* GPS Location */}
        {exif.gps_location && (
          <div className="exif-item">
            <span className="exif-label">GPS Coordinates</span>
            <span className="exif-value">
              {formatGPS(exif.gps_location.latitude, exif.gps_location.longitude)}
            </span>
          </div>
        )}

        {/* Camera Make */}
        {exif.camera_make && (
          <div className="exif-item">
            <span className="exif-label">Camera</span>
            <span className="exif-value">
              {exif.camera_make}
              {exif.camera_model && ` ${exif.camera_model}`}
            </span>
          </div>
        )}

        {/* Image Dimensions */}
        {exif.image_width && exif.image_height && (
          <div className="exif-item">
            <span className="exif-label">Dimensions</span>
            <span className="exif-value">
              {exif.image_width} × {exif.image_height} pixels
            </span>
          </div>
        )}

        {/* Focal Length */}
        {exif.focal_length && (
          <div className="exif-item">
            <span className="exif-label">Focal Length</span>
            <span className="exif-value">{exif.focal_length}</span>
          </div>
        )}

        {/* Aperture */}
        {exif.aperture && (
          <div className="exif-item">
            <span className="exif-label">Aperture</span>
            <span className="exif-value">{exif.aperture}</span>
          </div>
        )}

        {/* Shutter Speed */}
        {exif.shutter_speed && (
          <div className="exif-item">
            <span className="exif-label">Shutter Speed</span>
            <span className="exif-value">{exif.shutter_speed}</span>
          </div>
        )}

        {/* ISO */}
        {exif.iso && (
          <div className="exif-item">
            <span className="exif-label">ISO</span>
            <span className="exif-value">{exif.iso}</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default EXIFDisplay;
