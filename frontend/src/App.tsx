/**
 * StoneKeeper main application component.
 *
 * Sets up React Router and provides application-level state management.
 */
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import UploadPage from './pages/UploadPage';

/**
 * Main application component.
 */
const App: React.FC = () => {
  return (
    <Router>
      <div className="app">
        {/* Header / Navigation */}
        <header className="app-header">
          <div className="container">
            <h1 className="app-title">
              <Link to="/">StoneKeeper</Link>
            </h1>
            <nav className="app-nav">
              <Link to="/">Home</Link>
              <Link to="/cemeteries">Cemeteries</Link>
              <Link to="/search">Search</Link>
              <Link to="/upload">Upload</Link>
            </nav>
          </div>
        </header>

        {/* Main Content */}
        <main className="app-main">
          <div className="container">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/cemeteries" element={<CemeteriesPage />} />
              <Route path="/search" element={<SearchPage />} />
              <Route path="/upload" element={<UploadPage />} />
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </div>
        </main>

        {/* Footer */}
        <footer className="app-footer">
          <div className="container">
            <p>StoneKeeper v1.0.0 - Cemetery Photo Cataloging System</p>
          </div>
        </footer>
      </div>
    </Router>
  );
};

/**
 * Home page component.
 *
 * Landing page with quick actions and system overview.
 */
const HomePage: React.FC = () => {
  return (
    <div className="page home-page">
      <div className="hero">
        <h2>Welcome to StoneKeeper</h2>
        <p className="hero-description">
          A cemetery photo cataloging system designed for researchers and genealogists.
          Upload photos and automatically extract EXIF metadata including dates, GPS coordinates,
          and camera information.
        </p>
      </div>

      <div className="features">
        <div className="feature-card">
          <div className="feature-icon">📷</div>
          <h3>Automatic EXIF Extraction</h3>
          <p>
            Upload photos and we'll automatically extract date taken, GPS coordinates,
            camera settings, and more from the image metadata.
          </p>
        </div>

        <div className="feature-card">
          <div className="feature-icon">🗺️</div>
          <h3>GPS Mapping</h3>
          <p>
            Store and search by GPS coordinates. Find cemeteries and photos
            based on location data.
          </p>
        </div>

        <div className="feature-card">
          <div className="feature-icon">🔍</div>
          <h3>Searchable Database</h3>
          <p>
            Organize photos by cemetery, section, and plot. Search by name,
            date, location, and more.
          </p>
        </div>

        <div className="feature-card">
          <div className="feature-icon">💾</div>
          <h3>Data Integrity</h3>
          <p>
            Original photos are never modified. All data is preserved with
            soft deletes and comprehensive metadata.
          </p>
        </div>
      </div>

      <div className="quick-actions">
        <Link to="/upload" className="btn btn-primary">Upload Photo</Link>
        <Link to="/search" className="btn btn-secondary">Search Catalog</Link>
        <Link to="/cemeteries" className="btn btn-secondary">Browse Cemeteries</Link>
      </div>
    </div>
  );
};

/**
 * Placeholder cemeteries page component.
 * Will be implemented in User Story 4.
 */
const CemeteriesPage: React.FC = () => {
  return (
    <div className="page cemeteries-page">
      <h2>Cemeteries</h2>
      <p>Cemetery list and management will be available in a future update.</p>
      <Link to="/upload" className="btn btn-primary">Upload Photos</Link>
    </div>
  );
};

/**
 * Placeholder search page component.
 * Will be implemented in User Story 2.
 */
const SearchPage: React.FC = () => {
  return (
    <div className="page search-page">
      <h2>Search Photos</h2>
      <p>Search and browse functionality will be available in a future update.</p>
      <Link to="/upload" className="btn btn-primary">Upload Photos</Link>
    </div>
  );
};

/**
 * 404 Not Found page component.
 */
const NotFoundPage: React.FC = () => {
  return (
    <div className="page not-found-page">
      <h2>Page Not Found</h2>
      <p>The page you are looking for does not exist.</p>
      <Link to="/">Return to Home</Link>
    </div>
  );
};

export default App;
