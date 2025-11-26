# StoneKeeper Quickstart Guide

Welcome to StoneKeeper! This guide will help you deploy and start using the cemetery photo cataloging system in under 10 minutes.

## Prerequisites

Before you begin, ensure you have:
- **Docker** installed (version 20.10 or later)
- **Docker Compose** installed (version 2.0 or later)
- **2GB RAM** available
- **50GB disk space** for photos and database
- **Linux, macOS, or Windows** with WSL2

**Check your Docker installation:**
```bash
docker --version
docker-compose --version
```

## Quick Start (5 Steps)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourorg/stonekeeper.git
cd stonekeeper
```

### Step 2: Create Secrets

StoneKeeper uses Docker secrets to securely store passwords and keys.

```bash
# Create secrets directory
mkdir -p secrets

# Generate database password
openssl rand -base64 32 > secrets/db_password.txt

# Generate session secret key
openssl rand -base64 32 > secrets/session_secret.txt

# Create database username
echo "stonekeeper_user" > secrets/db_user.txt

# Secure the secrets (recommended)
chmod 600 secrets/*
```

**Windows users (without OpenSSL):**
```powershell
# PowerShell commands
New-Item -ItemType Directory -Path secrets -Force
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | % {[char]$_}) | Set-Content secrets/db_password.txt
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | % {[char]$_}) | Set-Content secrets/session_secret.txt
"stonekeeper_user" | Set-Content secrets/db_user.txt
```

### Step 3: Deploy with Docker Compose

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

**Expected output:**
```
NAME                           STATUS        PORTS
stonekeeper-postgres-1         Up            5432/tcp
stonekeeper-backend-1          Up            8000/tcp
stonekeeper-frontend-1         Up            0.0.0.0:80->80/tcp
```

### Step 4: Initialize Database

The database schema is created automatically on first startup. Check the logs to confirm:

```bash
docker-compose logs backend | grep "Database initialized"
```

### Step 5: Access StoneKeeper

Open your web browser and navigate to:

```
http://localhost
```

You should see the StoneKeeper login page!

---

## First-Time Setup

### Create Your Admin Account

1. Click **"Register"** on the login page
2. Fill in the registration form:
   - **Email**: Your email address
   - **Password**: At least 8 characters (use a strong password!)
   - **Full Name**: Your name for photographer attribution
3. Click **"Create Account"**
4. You'll be automatically logged in

### Upload Your First Photo

1. Click **"Add Cemetery"** to create your first cemetery:
   - **Name**: Cemetery name (e.g., "Oak Hill Cemetery")
   - **Location**: City, state, country (e.g., "Springfield, Illinois, USA")
   - **GPS Coordinates** (optional): Latitude and longitude
   - Click **"Save"**

2. Click **"Upload Photo"**:
   - **Select File**: Choose a cemetery photo (JPEG, PNG, or TIFF, max 20MB)
   - **Cemetery**: Select the cemetery you just created
   - **Description**: Describe what the photo shows
   - Click **"Upload"**

3. Wait 2-5 seconds while the system:
   - Uploads the file
   - Extracts EXIF metadata (date, GPS, camera info)
   - Generates thumbnails
   - Saves to the database

4. You'll see your photo in the gallery with extracted metadata!

### Search Your Photos

1. Use the search bar at the top:
   - Search by cemetery name: "Oak Hill"
   - Filter by date range: Select start and end dates
   - Filter by photographer: Select your name

2. Click any thumbnail to view:
   - Full-size image
   - Complete EXIF metadata
   - Cemetery, section, plot details
   - Upload information

3. Download original photo with metadata intact by clicking **"Download Original"**

---

## Common Tasks

### Add a Cemetery Section

1. Navigate to a cemetery page
2. Click **"Add Section"**
3. Enter:
   - **Name**: Section identifier (e.g., "Section A", "Veterans Area")
   - **Description**: Optional notes
4. Click **"Save"**

### Add a Burial Plot

1. Navigate to a section page
2. Click **"Add Plot"**
3. Enter:
   - **Plot Number**: Identifier (e.g., "A-101", "Row 5, Plot 12")
   - **Row**: Optional row identifier
   - **Headstone Inscription**: Transcribed text from headstone
   - **Burial Date**: Date if known
4. Click **"Save"**

### Associate Photos with Plots

1. Open a photo detail page
2. Click **"Edit Details"**
3. Select:
   - **Section**: The cemetery section
   - **Plot**: The specific burial plot
4. Click **"Save"**

Now the photo is linked to the plot for organized browsing!

### Invite Additional Researchers

1. Share the StoneKeeper URL with your team: `http://your-server-address`
2. Each researcher creates their own account
3. All users share the same photo catalog
4. Photos show photographer attribution automatically

---

## Troubleshooting

### Problem: Cannot access http://localhost

**Check if services are running:**
```bash
docker-compose ps
```

**View logs:**
```bash
docker-compose logs
```

**Common solutions:**
- Ensure port 80 is not already in use
- Check Docker Desktop is running (Windows/Mac)
- Try accessing via `http://127.0.0.1`

### Problem: Database connection errors

**Restart the database:**
```bash
docker-compose restart postgres
docker-compose restart backend
```

**Check database logs:**
```bash
docker-compose logs postgres
```

### Problem: Photo upload fails

**Check photo requirements:**
- File format: JPEG, PNG, or TIFF only
- File size: Maximum 20MB
- File not corrupted: Open in another app to verify

**Check backend logs:**
```bash
docker-compose logs backend
```

### Problem: EXIF data not extracted

**Note**: Not all photos contain EXIF metadata. Photos taken with some cameras or edited with certain software may have EXIF stripped.

**Solution**: You can manually enter date and location information when uploading.

### Problem: Slow performance

**Check resource usage:**
```bash
docker stats
```

**Recommended fixes:**
- Ensure adequate RAM (2GB minimum, 4GB recommended)
- Check available disk space: `df -h`
- Limit photo uploads to batches of 50-100 at a time

---

## Stopping and Starting

### Stop StoneKeeper

```bash
# Stop all services (preserves data)
docker-compose stop

# Or completely remove containers (preserves data in volumes)
docker-compose down
```

### Start StoneKeeper

```bash
# Start existing containers
docker-compose start

# Or recreate containers if needed
docker-compose up -d
```

**Note**: Your photos and database are stored in Docker volumes and persist even when containers are removed.

---

## Backup and Restore

### Backup Your Data

It's important to regularly backup your cemetery photos and database!

**Run the backup script:**
```bash
./scripts/backup.sh
```

This creates a timestamped backup directory with:
- `photos.tar.gz`: All your cemetery photos
- `database.sql.gz`: Complete database dump

**Manual backup:**
```bash
# Backup photos
docker run --rm \
  -v stonekeeper_photo-storage:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/photos-$(date +%Y%m%d).tar.gz -C /data .

# Backup database
docker exec stonekeeper_postgres_1 pg_dump -U stonekeeper_user stonekeeper \
  | gzip > backups/database-$(date +%Y%m%d).sql.gz
```

### Restore from Backup

**Run the restore script:**
```bash
./scripts/restore.sh /path/to/backup-directory
```

**Manual restore:**
```bash
# Restore photos
docker run --rm \
  -v stonekeeper_photo-storage:/data \
  -v /path/to/backup:/backup \
  alpine tar xzf /backup/photos.tar.gz -C /data

# Restore database
gunzip < /path/to/backup/database.sql.gz | \
  docker exec -i stonekeeper_postgres_1 psql -U stonekeeper_user stonekeeper
```

---

## Configuration

### Change the Port

By default, StoneKeeper runs on port 80. To use a different port:

**Edit `docker-compose.yml`:**
```yaml
frontend:
  ports:
    - "8080:80"  # Change 8080 to your desired port
```

**Restart:**
```bash
docker-compose down
docker-compose up -d
```

**Access at:** `http://localhost:8080`

### Enable HTTPS (Production)

For production deployments with a domain name:

1. Install a reverse proxy (nginx, Traefik, Caddy)
2. Configure SSL certificates (Let's Encrypt recommended)
3. Point the proxy to `http://localhost:80`

**Example nginx configuration:**
```nginx
server {
    listen 443 ssl;
    server_name stonekeeper.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Increase Storage Limits

**Photo file size limit** (default 20MB):

Edit `backend/src/main.py`:
```python
MAX_PHOTO_SIZE = 20 * 1024 * 1024  # Change to desired bytes
```

**Database storage**:
PostgreSQL automatically uses available disk space. Monitor with:
```bash
docker exec stonekeeper_postgres_1 psql -U stonekeeper_user -c "SELECT pg_size_pretty(pg_database_size('stonekeeper'));"
```

---

## System Requirements

### Minimum Requirements
- 2GB RAM
- 50GB disk space (accommodates ~5,000 photos at 10MB each)
- Dual-core CPU

### Recommended Requirements
- 4GB RAM
- 500GB disk space (accommodates ~50,000 photos)
- Quad-core CPU
- SSD storage for better performance

### Scaling Guidelines

| Photos    | RAM  | Disk Space | Concurrent Users |
|-----------|------|------------|------------------|
| 1,000     | 2GB  | 10GB       | 5-10             |
| 10,000    | 2GB  | 100GB      | 10-20            |
| 50,000    | 4GB  | 500GB      | 20-50            |
| 100,000   | 8GB  | 1TB        | 50-100           |

---

## Getting Help

### View Logs

**All services:**
```bash
docker-compose logs
```

**Specific service:**
```bash
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres
```

**Follow logs in real-time:**
```bash
docker-compose logs -f
```

### Check System Health

```bash
# Container status
docker-compose ps

# Resource usage
docker stats

# Disk space
df -h

# Database connections
docker exec stonekeeper_postgres_1 psql -U stonekeeper_user -c "SELECT count(*) FROM pg_stat_activity;"
```

### Report Issues

If you encounter bugs or need assistance:
1. Check the [GitHub Issues](https://github.com/yourorg/stonekeeper/issues)
2. Include:
   - Your operating system
   - Docker version: `docker --version`
   - Error messages from logs
   - Steps to reproduce the issue

---

## Next Steps

Now that StoneKeeper is running, you can:

1. **Invite your research team** - Share the URL and have them create accounts
2. **Add your cemeteries** - Document the cemeteries you're researching
3. **Upload photos** - Start building your photo catalog
4. **Organize by section and plot** - Structure your cemetery documentation
5. **Search and browse** - Find photos by cemetery, date, or photographer
6. **Download and share** - Export photos with metadata preserved

---

## Advanced Topics

### Custom Domain Setup

1. Register a domain name
2. Point DNS A record to your server IP
3. Configure reverse proxy with SSL (see HTTPS section above)
4. Update `frontend/src/config.js` with your domain

### Multi-Organization Deployment

Each organization should run their own StoneKeeper instance for data privacy:

1. Clone repository for each organization
2. Use different ports for each instance
3. Configure separate Docker networks
4. Maintain separate backups

### Database Migrations

StoneKeeper uses Alembic for database schema migrations:

```bash
# Run migrations
docker exec stonekeeper_backend_1 alembic upgrade head

# View migration history
docker exec stonekeeper_backend_1 alembic history

# Rollback one migration
docker exec stonekeeper_backend_1 alembic downgrade -1
```

---

## Success Criteria Checklist

Verify your installation meets the project's success criteria:

- [ ] Photo upload with EXIF extraction completes in <5 seconds
- [ ] Search results return in <1 second for your current catalog size
- [ ] You successfully uploaded your first photo in <5 minutes
- [ ] Gallery pages load in <2 seconds
- [ ] All cemetery data is preserved (no data loss)
- [ ] Deployment completed in <10 minutes following this guide
- [ ] System is accessible and responsive
- [ ] Photos display correctly with thumbnails

---

**Congratulations!** You're now ready to use StoneKeeper for cemetery photo cataloging.

For detailed information about features and API usage, see the [User Manual](docs/user-manual.md) and [API Documentation](docs/api.md).
