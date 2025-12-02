/**
 * PhotoDetail component for StoneKeeper.
 *
 * Displays full photo with complete metadata.
 */
import React from 'react';
import { getPhotoPreviewUrl, getPhotoFileUrl } from '../../services/api';
import type { Photograph } from '../../types';
import EXIFDisplay from '../EXIFDisplay';
import './styles.css';

interface PhotoDetailProps {
  photo: Photograph;
  onClose?: () => void;
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
 * Format file size for display.
 */
const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} bytes`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
};

/**
 * Photo detail component with full metadata display.
 *
 * Shows photo with all available metadata including EXIF data,
 * user-provided descriptions, and uploader attribution.
 */
const PhotoDetail: React.FC<PhotoDetailProps> = ({ photo, onClose }) => {
  const previewUrl = getPhotoPreviewUrl(photo.id);
  const downloadUrl = getPhotoFileUrl(photo.id);

  return (
    <div className="photo-detail">
      {onClose && (
        <button className="btn-close" onClick={onClose} aria-label="Close">
          ✕
        </button>
      )}

      {/* Photo Image */}
      <div className="photo-container">
        <img
          src={previewUrl}
          alt={photo.description || 'Cemetery photo'}
          className="photo-image"
        />
      </div>

      {/* Photo Actions */}
      <div className="photo-actions">
        <a
          href={downloadUrl}
          download
          className="btn btn-secondary"
          target="_blank"
          rel="noopener noreferrer"
        >
          Download Original
        </a>
      </div>

      {/* Photo Metadata */}
      <div className="photo-metadata">
        {/* User-provided description */}
        {photo.description && (
          <div className="metadata-section">
            <h3 className="metadata-title">Description</h3>
            <p className="metadata-text">{photo.description}</p>
          </div>
        )}

        {/* Photographer notes */}
        {photo.photographer_notes && (
          <div className="metadata-section">
            <h3 className="metadata-title">Photographer Notes</h3>
            <p className="metadata-text">{photo.photographer_notes}</p>
          </div>
        )}

        {/* File information */}
        <div className="metadata-section">
          <h3 className="metadata-title">File Information</h3>
          <div className="info-grid">
            <div className="info-item">
              <span className="info-label">Format</span>
              <span className="info-value">{photo.file_format}</span>
            </div>
            <div className="info-item">
              <span className="info-label">File Size</span>
              <span className="info-value">{formatFileSize(photo.file_size_bytes)}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Photo ID</span>
              <span className="info-value">{photo.uuid}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Uploaded</span>
              <span className="info-value">{formatDate(photo.created_at)}</span>
            </div>
            {photo.uploader_name && (
              <div className="info-item">
                <span className="info-label">Uploaded By</span>
                <span className="info-value">{photo.uploader_name}</span>
              </div>
            )}
          </div>
        </div>

        {/* EXIF Metadata */}
        {photo.exif_metadata && (
          <div className="metadata-section">
            <EXIFDisplay exif={photo.exif_metadata} />
          </div>
        )}
      </div>
    </div>
  );
};

export default PhotoDetail;
