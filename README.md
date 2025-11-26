# StoneKeeper

A web application for cataloging cemetery photographs with automatic EXIF metadata extraction, searchable database, and Docker deployment.

## Features

- **Photo Upload**: Upload cemetery photos with automatic EXIF metadata extraction (date, GPS, camera info)
- **Search & Browse**: Search photos by cemetery name, location, date range, and photographer
- **Multi-User Collaboration**: Multiple researchers can work together with photographer attribution
- **Cemetery Organization**: Organize photos by cemetery structure (sections, rows, plots)
- **Docker Deployment**: Easy self-hosted deployment with Docker Compose

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- 2GB RAM available
- 50GB disk space for photos and database

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourorg/stonekeeper.git
cd stonekeeper
```

2. Create secrets:
```bash
mkdir -p secrets
echo "stonekeeper_user" > secrets/db_user.txt
openssl rand -base64 32 > secrets/db_password.txt
openssl rand -base64 32 > secrets/session_secret.txt
chmod 600 secrets/*
```

3. Deploy with Docker Compose:
```bash
docker-compose up -d
```

4. Access StoneKeeper:
Open your browser to `http://localhost`

### First-Time Setup

On first access, you'll be guided through creating an admin account.

## Technology Stack

**Backend**:
- Python 3.11+ with FastAPI
- PostgreSQL 15+ with PostGIS
- SQLAlchemy ORM
- Pillow for EXIF extraction

**Frontend**:
- React 18+ with TypeScript
- React Router for navigation
- Axios for API calls

**Deployment**:
- Docker Compose orchestration
- Multi-stage Docker builds
- Named volumes for data persistence

## Project Structure

```
stonekeeper/
├── backend/          # Python FastAPI backend
│   ├── src/
│   │   ├── models/   # Database models
│   │   ├── services/ # Business logic
│   │   ├── api/      # API endpoints
│   │   └── db/       # Database configuration
│   └── requirements.txt
├── frontend/         # React TypeScript frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── types/
│   └── package.json
├── docs/             # Documentation
└── docker-compose.yml
```

## Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

## Documentation

- [Quickstart Guide](specs/001-photo-cataloging/quickstart.md)
- [API Documentation](specs/001-photo-cataloging/contracts/api.yaml)
- [Data Model](specs/001-photo-cataloging/data-model.md)
- [Architecture Decisions](docs/adr/)

## Constitution Principles

StoneKeeper is built on four core principles:

1. **Data Integrity First**: Cemetery records are irreplaceable historical artifacts
2. **Non-Technical User Focus**: Intuitive interface for researchers without technical expertise
3. **Maintainability & Simplicity**: Simple, well-documented code for long-term sustainability
4. **Preservation-Grade Documentation**: Archival-quality documentation

See [Constitution](/.specify/memory/constitution.md) for details.

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting pull requests.

## License

MIT License - see LICENSE file for details

## Support

For issues and questions, please create an issue on GitHub
