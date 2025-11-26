"""initial schema with PostGIS and all tables

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable PostGIS and UUID extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS postgis')
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm')  # For full-text search

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_deleted_at', 'users', ['deleted_at'])

    # Create user_sessions table
    op.create_table(
        'user_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_activity', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('ip_address', sa.String(45), nullable=True),  # IPv6 support
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_id')
    )
    op.create_index('ix_user_sessions_session_id', 'user_sessions', ['session_id'])
    op.create_index('ix_user_sessions_user_id', 'user_sessions', ['user_id'])
    op.create_index('ix_user_sessions_expires_at', 'user_sessions', ['expires_at'])

    # Create cemeteries table with PostGIS GEOGRAPHY type
    op.create_table(
        'cemeteries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('location_description', sa.Text(), nullable=True),
        sa.Column('gps_location', postgresql.GEOGRAPHY('POINT', srid=4326), nullable=True),
        sa.Column('established_year', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_cemeteries_name', 'cemeteries', ['name'])
    op.create_index('ix_cemeteries_deleted_at', 'cemeteries', ['deleted_at'])
    # Spatial index for GPS location using GIST
    op.execute('CREATE INDEX ix_cemeteries_gps_location ON cemeteries USING GIST (gps_location)')

    # Create sections table
    op.create_table(
        'sections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cemetery_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['cemetery_id'], ['cemeteries.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_sections_cemetery_id', 'sections', ['cemetery_id'])
    op.create_index('ix_sections_deleted_at', 'sections', ['deleted_at'])

    # Create plots table
    op.create_table(
        'plots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('section_id', sa.Integer(), nullable=False),
        sa.Column('plot_number', sa.String(50), nullable=True),
        sa.Column('row_identifier', sa.String(50), nullable=True),
        sa.Column('headstone_inscription', sa.Text(), nullable=True),
        sa.Column('burial_date', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['section_id'], ['sections.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_plots_section_id', 'plots', ['section_id'])
    op.create_index('ix_plots_deleted_at', 'plots', ['deleted_at'])

    # Create photographs table with EXIF metadata
    op.create_table(
        'photographs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('cemetery_id', sa.Integer(), nullable=False),
        sa.Column('section_id', sa.Integer(), nullable=True),
        sa.Column('plot_id', sa.Integer(), nullable=True),

        # File information
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('thumbnail_path', sa.String(500), nullable=True),
        sa.Column('preview_path', sa.String(500), nullable=True),
        sa.Column('file_size_bytes', sa.BigInteger(), nullable=False),
        sa.Column('file_format', sa.String(10), nullable=False),  # JPEG, PNG, TIFF

        # EXIF metadata
        sa.Column('exif_date_taken', sa.DateTime(timezone=True), nullable=True),
        sa.Column('exif_gps_location', postgresql.GEOGRAPHY('POINT', srid=4326), nullable=True),
        sa.Column('exif_camera_make', sa.String(100), nullable=True),
        sa.Column('exif_camera_model', sa.String(100), nullable=True),
        sa.Column('exif_focal_length', sa.String(50), nullable=True),
        sa.Column('exif_aperture', sa.String(50), nullable=True),
        sa.Column('exif_shutter_speed', sa.String(50), nullable=True),
        sa.Column('exif_iso', sa.Integer(), nullable=True),
        sa.Column('image_width', sa.Integer(), nullable=True),
        sa.Column('image_height', sa.Integer(), nullable=True),

        # User-provided metadata
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('photographer_notes', sa.Text(), nullable=True),

        # Tracking
        sa.Column('uploaded_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),

        sa.ForeignKeyConstraint(['cemetery_id'], ['cemeteries.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['section_id'], ['sections.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['plot_id'], ['plots.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid')
    )
    op.create_index('ix_photographs_uuid', 'photographs', ['uuid'])
    op.create_index('ix_photographs_cemetery_id', 'photographs', ['cemetery_id'])
    op.create_index('ix_photographs_section_id', 'photographs', ['section_id'])
    op.create_index('ix_photographs_plot_id', 'photographs', ['plot_id'])
    op.create_index('ix_photographs_uploaded_by', 'photographs', ['uploaded_by'])
    op.create_index('ix_photographs_exif_date_taken', 'photographs', ['exif_date_taken'])
    op.create_index('ix_photographs_deleted_at', 'photographs', ['deleted_at'])
    # Spatial index for EXIF GPS location
    op.execute('CREATE INDEX ix_photographs_exif_gps_location ON photographs USING GIST (exif_gps_location)')

    # Full-text search indexes using gin_trgm_ops for partial matching
    op.execute('CREATE INDEX ix_cemeteries_name_trgm ON cemeteries USING gin (name gin_trgm_ops)')
    op.execute('CREATE INDEX ix_plots_inscription_trgm ON plots USING gin (headstone_inscription gin_trgm_ops)')
    op.execute('CREATE INDEX ix_photographs_description_trgm ON photographs USING gin (description gin_trgm_ops)')

    # Create trigger function for automatic updated_at timestamp
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)

    # Apply updated_at triggers to all tables
    op.execute("""
        CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)
    op.execute("""
        CREATE TRIGGER update_cemeteries_updated_at BEFORE UPDATE ON cemeteries
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)
    op.execute("""
        CREATE TRIGGER update_sections_updated_at BEFORE UPDATE ON sections
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)
    op.execute("""
        CREATE TRIGGER update_plots_updated_at BEFORE UPDATE ON plots
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)
    op.execute("""
        CREATE TRIGGER update_photographs_updated_at BEFORE UPDATE ON photographs
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    # Drop triggers
    op.execute('DROP TRIGGER IF EXISTS update_photographs_updated_at ON photographs')
    op.execute('DROP TRIGGER IF EXISTS update_plots_updated_at ON plots')
    op.execute('DROP TRIGGER IF EXISTS update_sections_updated_at ON sections')
    op.execute('DROP TRIGGER IF EXISTS update_cemeteries_updated_at ON cemeteries')
    op.execute('DROP TRIGGER IF EXISTS update_users_updated_at ON users')

    # Drop trigger function
    op.execute('DROP FUNCTION IF EXISTS update_updated_at_column()')

    # Drop tables in reverse order of creation (respecting foreign keys)
    op.drop_table('photographs')
    op.drop_table('plots')
    op.drop_table('sections')
    op.drop_table('cemeteries')
    op.drop_table('user_sessions')
    op.drop_table('users')

    # Extensions are typically not dropped to avoid affecting other databases
    # op.execute('DROP EXTENSION IF EXISTS pg_trgm')
    # op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')
    # op.execute('DROP EXTENSION IF EXISTS postgis')
