/**
 * PhotoUpload component for StoneKeeper.
 *
 * Handles photo file upload with drag-and-drop, validation, and progress tracking.
 */
import React, { useState, useRef, useEffect } from 'react';
import { uploadPhoto } from '../../services/api';
import type { Cemetery, Section, Plot, Photograph, PhotoUpload as PhotoUploadData } from '../../types';
import './styles.css';

interface PhotoUploadProps {
  cemeteries: Cemetery[];
  onUploadSuccess: (photo: Photograph) => void;
  onUploadError: (error: string) => void;
}

const MAX_FILE_SIZE = 20 * 1024 * 1024; // 20MB
const ALLOWED_FORMATS = ['image/jpeg', 'image/png', 'image/tiff'];
const ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.tiff', '.tif'];

/**
 * Photo upload component with drag-and-drop support.
 *
 * Per Constitution Principle II: User-friendly interface with clear
 * validation messages and progress feedback.
 */
const PhotoUpload: React.FC<PhotoUploadProps> = ({
  cemeteries,
  onUploadSuccess,
  onUploadError
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);

  // Form fields
  const [cemeteryId, setCemeteryId] = useState<number | ''>('');
  const [sectionId, setSectionId] = useState<number | ''>('');
  const [plotId, setPlotId] = useState<number | ''>('');
  const [description, setDescription] = useState('');
  const [photographerNotes, setPhotographerNotes] = useState('');

  // Sections and plots for selected cemetery
  const [sections, setSections] = useState<Section[]>([]);
  const [plots, setPlots] = useState<Plot[]>([]);

  const fileInputRef = useRef<HTMLInputElement>(null);

  /**
   * Load sections when cemetery is selected.
   */
  useEffect(() => {
    if (cemeteryId) {
      // TODO: Load sections from API
      // For now, sections will be loaded in future user stories
      setSections([]);
      setSectionId('');
      setPlotId('');
    }
  }, [cemeteryId]);

  /**
   * Load plots when section is selected.
   */
  useEffect(() => {
    if (sectionId) {
      // TODO: Load plots from API
      // For now, plots will be loaded in future user stories
      setPlots([]);
      setPlotId('');
    }
  }, [sectionId]);

  /**
   * Validate file type and size.
   */
  const validateFile = (file: File): { valid: boolean; error?: string } => {
    // Check file type
    if (!ALLOWED_FORMATS.includes(file.type)) {
      const ext = '.' + file.name.split('.').pop()?.toLowerCase();
      if (!ALLOWED_EXTENSIONS.includes(ext || '')) {
        return {
          valid: false,
          error: `Invalid file type. Please upload a JPEG, PNG, or TIFF image. Your file is: ${file.type || 'unknown'}`
        };
      }
    }

    // Check file size
    if (file.size > MAX_FILE_SIZE) {
      const sizeMB = (file.size / (1024 * 1024)).toFixed(1);
      return {
        valid: false,
        error: `File too large. Maximum size is 20MB. Your file is ${sizeMB}MB.`
      };
    }

    return { valid: true };
  };

  /**
   * Handle file selection.
   */
  const handleFileSelect = (file: File) => {
    const validation = validateFile(file);

    if (!validation.valid) {
      onUploadError(validation.error!);
      return;
    }

    setSelectedFile(file);

    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(reader.result as string);
    };
    reader.readAsDataURL(file);
  };

  /**
   * Handle file input change.
   */
  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  /**
   * Handle drag over.
   */
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  /**
   * Handle drag leave.
   */
  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  /**
   * Handle file drop.
   */
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const file = e.dataTransfer.files[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  /**
   * Clear selected file.
   */
  const clearFile = () => {
    setSelectedFile(null);
    setPreview(null);
    setUploadProgress(0);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  /**
   * Handle upload.
   */
  const handleUpload = async () => {
    if (!selectedFile) {
      onUploadError('Please select a file to upload');
      return;
    }

    if (!cemeteryId) {
      onUploadError('Please select a cemetery');
      return;
    }

    const metadata: PhotoUploadData = {
      cemetery_id: cemeteryId as number,
      section_id: sectionId || undefined,
      plot_id: plotId || undefined,
      description: description || undefined,
      photographer_notes: photographerNotes || undefined
    };

    setIsUploading(true);
    setUploadProgress(0);

    try {
      const photo = await uploadPhoto(selectedFile, metadata, (progress) => {
        setUploadProgress(progress);
      });

      onUploadSuccess(photo);

      // Reset form
      clearFile();
      setDescription('');
      setPhotographerNotes('');
      setCemeteryId('');
      setSectionId('');
      setPlotId('');

    } catch (error: any) {
      const errorMessage = error.response?.data?.message || error.message || 'Upload failed';
      onUploadError(errorMessage);
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  return (
    <div className="photo-upload">
      {/* File Drop Zone */}
      <div
        className={`drop-zone ${isDragging ? 'dragging' : ''} ${selectedFile ? 'has-file' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !selectedFile && fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={ALLOWED_EXTENSIONS.join(',')}
          onChange={handleFileInputChange}
          style={{ display: 'none' }}
          disabled={isUploading}
        />

        {!selectedFile ? (
          <div className="drop-zone-content">
            <div className="upload-icon">📷</div>
            <p className="drop-zone-text">
              <strong>Click to select</strong> or drag and drop a photo here
            </p>
            <p className="drop-zone-hint">
              JPEG, PNG, or TIFF • Max 20MB
            </p>
          </div>
        ) : (
          <div className="preview-container">
            <img src={preview!} alt="Preview" className="preview-image" />
            <div className="file-info">
              <p className="file-name">{selectedFile.name}</p>
              <p className="file-size">
                {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
              </p>
            </div>
            {!isUploading && (
              <button
                type="button"
                className="btn-remove"
                onClick={(e) => {
                  e.stopPropagation();
                  clearFile();
                }}
              >
                Remove
              </button>
            )}
          </div>
        )}
      </div>

      {/* Upload Progress */}
      {isUploading && (
        <div className="upload-progress">
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
          <p className="progress-text">Uploading... {uploadProgress}%</p>
        </div>
      )}

      {/* Metadata Form */}
      <div className="upload-form">
        <div className="form-group">
          <label htmlFor="cemetery" className="required">Cemetery</label>
          <select
            id="cemetery"
            value={cemeteryId}
            onChange={(e) => setCemeteryId(e.target.value ? parseInt(e.target.value) : '')}
            disabled={isUploading}
            required
          >
            <option value="">Select a cemetery</option>
            {cemeteries.map((cemetery) => (
              <option key={cemetery.id} value={cemetery.id}>
                {cemetery.name}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="section">Section (optional)</label>
          <select
            id="section"
            value={sectionId}
            onChange={(e) => setSectionId(e.target.value ? parseInt(e.target.value) : '')}
            disabled={isUploading || !cemeteryId || sections.length === 0}
          >
            <option value="">No specific section</option>
            {sections.map((section) => (
              <option key={section.id} value={section.id}>
                {section.name}
              </option>
            ))}
          </select>
          {cemeteryId && sections.length === 0 && (
            <span className="help-text">No sections available for this cemetery</span>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="plot">Plot (optional)</label>
          <select
            id="plot"
            value={plotId}
            onChange={(e) => setPlotId(e.target.value ? parseInt(e.target.value) : '')}
            disabled={isUploading || !sectionId || plots.length === 0}
          >
            <option value="">No specific plot</option>
            {plots.map((plot) => (
              <option key={plot.id} value={plot.id}>
                {plot.plot_number || `Plot ${plot.id}`}
              </option>
            ))}
          </select>
          {sectionId && plots.length === 0 && (
            <span className="help-text">No plots available for this section</span>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="description">Description (optional)</label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Brief description of what this photo shows"
            rows={3}
            disabled={isUploading}
          />
        </div>

        <div className="form-group">
          <label htmlFor="photographer_notes">Photographer Notes (optional)</label>
          <textarea
            id="photographer_notes"
            value={photographerNotes}
            onChange={(e) => setPhotographerNotes(e.target.value)}
            placeholder="Additional notes, lighting conditions, etc."
            rows={3}
            disabled={isUploading}
          />
        </div>

        <button
          type="button"
          className="btn btn-primary btn-upload"
          onClick={handleUpload}
          disabled={!selectedFile || !cemeteryId || isUploading}
        >
          {isUploading ? 'Uploading...' : 'Upload Photo'}
        </button>
      </div>
    </div>
  );
};

export default PhotoUpload;
