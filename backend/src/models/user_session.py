"""
User session model for StoneKeeper authentication.

Manages session-based authentication with HTTP-only cookies,
avoiding JWT complexities per research.md decision.
"""
from datetime import datetime
from uuid import UUID

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from src.db.base import Base


class UserSession(Base):
    """
    User authentication session.

    Sessions are created on login and validated on each request.
    Session ID is stored in an HTTP-only cookie on the client.

    Attributes:
        id: Primary key
        session_id: UUID for session identification (stored in cookie)
        user_id: Foreign key to users table
        created_at: Session creation timestamp
        expires_at: Session expiration timestamp (7 days by default)
        last_activity: Last request timestamp (updated on each request)
        ip_address: Client IP address for security tracking
        user_agent: Client user agent for security tracking

    Relationships:
        user: The user this session belongs to
    """

    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(PG_UUID(as_uuid=True), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    last_activity = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # Security tracking
    ip_address = Column(String(45), nullable=True)  # IPv6 support (max 45 chars)
    user_agent = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="sessions")

    def __repr__(self) -> str:
        return f"<UserSession(id={self.id}, user_id={self.user_id}, session_id='{self.session_id}')>"

    @property
    def is_expired(self) -> bool:
        """Check if session has expired."""
        return datetime.utcnow() > self.expires_at
