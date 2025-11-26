/**
 * StoneKeeper main application component.
 *
 * Sets up React Router and provides application-level state management.
 */
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';

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
 * Placeholder home page component.
 */
const HomePage: React.FC = () => {
  return (
    <div className="page home-page">
      <h2>Welcome to StoneKeeper</h2>
      <p>
        StoneKeeper helps researchers catalog cemetery photographs with automatic
        metadata extraction and searchable database.
      </p>
      <div className="quick-actions">
        <Link to="/upload" className="btn btn-primary">Upload Photo</Link>
        <Link to="/search" className="btn btn-secondary">Search Catalog</Link>
      </div>
    </div>
  );
};

/**
 * Placeholder cemeteries page component.
 */
const CemeteriesPage: React.FC = () => {
  return (
    <div className="page cemeteries-page">
      <h2>Cemeteries</h2>
      <p>Cemetery list will be displayed here.</p>
    </div>
  );
};

/**
 * Placeholder search page component.
 */
const SearchPage: React.FC = () => {
  return (
    <div className="page search-page">
      <h2>Search Photos</h2>
      <p>Search interface will be displayed here.</p>
    </div>
  );
};

/**
 * Placeholder upload page component.
 */
const UploadPage: React.FC = () => {
  return (
    <div className="page upload-page">
      <h2>Upload Photo</h2>
      <p>Photo upload form will be displayed here.</p>
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
