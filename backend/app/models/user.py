"""
User Model
Database model for farmer user accounts and profiles
"""

import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ARRAY, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):
    """User model representing farmer accounts"""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    name = Column(String(255), nullable=True)

    # Language and location preferences
    preferred_language = Column(String(2), default='en', nullable=False)  # 'en' or 'hi'
    location_state = Column(String(100), default='Jharkhand', nullable=False)
    location_district = Column(String(100), nullable=True)

    # Farm details
    land_size = Column(Numeric(10, 2), nullable=True)  # in hectares
    primary_crops = Column(ARRAY(String), nullable=True)  # array of crop names
    is_farmer = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, phone={self.phone_number}, name={self.name})>"

    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            "id": str(self.id),
            "phone_number": self.phone_number,
            "email": self.email,
            "name": self.name,
            "preferred_language": self.preferred_language,
            "location": {
                "state": self.location_state,
                "district": self.location_district
            },
            "farm_details": {
                "land_size_hectares": float(self.land_size) if self.land_size else None,
                "primary_crops": self.primary_crops or []
            },
            "is_farmer": self.is_farmer,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }