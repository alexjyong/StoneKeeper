/**
 * UploadPage for StoneKeeper.
 *
 * Allows users to upload cemetery photos with metadata.
 */
import React, { useState, useEffect } from 'react';
import CemeteryForm from '../components/CemeteryForm';
import PhotoUpload from '../components/PhotoUpload';
import { getCemeteries, createCemetery } from '../services/api';
import { getErrorMessage } from '../services/api';
import type { Cemetery, CemeteryCreate, Photograph } from '../types';
import './UploadPage.css';

/**
 * Upload page component.
 *
 * Provides interface for uploading photos and creating cemeteries.
 * Per Constitution Principle II: User-friendly with clear error messages.
 */
const UploadPage: React.FC = () => {

  const [cemeteries, setCemeteries] = useState<Cemetery[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [showCemeteryForm, setShowCemeteryForm] = useState(false);

  /**
   * Load cemeteries on mount.
   */
  useEffect(() => {
    loadCemeteries();
  }, []);

  /**
   * Load cemeteries from API.
   */
  const loadCemeteries = async () => {
    try {
      setLoading(true);
      const response = await getCemeteries(1, 100); // Get first 100 cemeteries
      setCemeteries(response.items);
    } catch (err: any) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle cemetery creation.
   */
  const handleCreateCemetery = async (cemeteryData: CemeteryCreate) => {
    try {
      const newCemetery = await createCemetery(cemeteryData);
      setCemeteries(prev => [...prev, newCemetery]);
      setShowCemeteryForm(false);
      setSuccess(`Cemetery "${newCemetery.name}" created successfully!`);
      setError(null);

      // Clear success message after 5 seconds
      setTimeout(() => setSuccess(null), 5000);
    } catch (err: any) {
      throw err; // Let CemeteryForm handle the error
    }
  };

  /**
   * Handle photo upload success.
   */
  const handleUploadSuccess = (_photo: Photograph) => {
    setSuccess('Photo uploaded successfully! EXIF data has been extracted.');
    setError(null);

    // Clear success message after 5 seconds
    setTimeout(() => setSuccess(null), 5000);

    // Future enhancement: navigate to photo detail page
    // navigate(`/photos/${_photo.id}`);
  };

  /**
   * Handle photo upload error.
   */
  const handleUploadError = (errorMessage: string) => {
    setError(errorMessage);
    setSuccess(null);

    // Scroll to top to show error
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  /**
   * Clear error message.
   */
  const clearError = () => {
    setError(null);
  };

  /**
   * Clear success message.
   */
  const clearSuccess = () => {
    setSuccess(null);
  };

  if (loading) {
    return (
      <div className="upload-page">
        <div className="loading">Loading cemeteries...</div>
      </div>
    );
  }

  return (
    <div className="upload-page">
      <div className="page-header">
        <h1>Upload Cemetery Photo</h1>
        <p className="page-description">
          Upload photos with automatic EXIF metadata extraction.
          Select or create a cemetery to get started.
        </p>
      </div>

      {/* Success Message */}
      {success && (
        <div className="alert alert-success">
          <span>{success}</span>
          <button
            className="alert-close"
            onClick={clearSuccess}
            aria-label="Close"
          >
            ✕
          </button>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="alert alert-error">
          <span>{error}</span>
          <button
            className="alert-close"
            onClick={clearError}
            aria-label="Close"
          >
            ✕
          </button>
        </div>
      )}

      {/* Cemetery Section */}
      <div className="section">
        <div className="section-header">
          <h2>Select Cemetery</h2>
          {!showCemeteryForm && (
            <button
              className="btn btn-secondary"
              onClick={() => setShowCemeteryForm(true)}
            >
              + Add New Cemetery
            </button>
          )}
        </div>

        {showCemeteryForm && (
          <div className="cemetery-form-container">
            <h3>Create New Cemetery</h3>
            <CemeteryForm
              onSubmit={handleCreateCemetery}
              onCancel={() => setShowCemeteryForm(false)}
              submitLabel="Create Cemetery"
            />
          </div>
        )}

        {cemeteries.length === 0 && !showCemeteryForm && (
          <div className="empty-state">
            <p>No cemeteries available. Create one to get started.</p>
            <button
              className="btn btn-primary"
              onClick={() => setShowCemeteryForm(true)}
            >
              Create First Cemetery
            </button>
          </div>
        )}
      </div>

      {/* Photo Upload Section */}
      {cemeteries.length > 0 && (
        <div className="section">
          <h2>Upload Photo</h2>
          <PhotoUpload
            cemeteries={cemeteries}
            onUploadSuccess={handleUploadSuccess}
            onUploadError={handleUploadError}
          />
        </div>
      )}
    </div>
  );
};

export default UploadPage;
