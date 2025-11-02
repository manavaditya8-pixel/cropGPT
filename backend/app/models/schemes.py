"""
Schemes Models
Database models for government farmer welfare schemes
"""

import uuid
from sqlalchemy import Column, String, DateTime, Date, Numeric, Boolean, Text, ARRAY, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class GovernmentScheme(Base):
    """Government welfare scheme model for farmers"""

    __tablename__ = "government_schemes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scheme_code = Column(String(100), unique=True, nullable=False, index=True)

    # Basic information
    name = Column(String(500), nullable=False)
    name_hi = Column(String(500), nullable=True)
    description = Column(Text, nullable=False)
    description_hi = Column(Text, nullable=True)

    # Categorization
    category = Column(String(100), nullable=False, index=True)  # 'financial_assistance', 'insurance', 'subsidy'
    implementing_agency = Column(String(255), nullable=True)

    # Financial details
    benefit_amount = Column(Numeric(12, 2), nullable=True)
    benefit_frequency = Column(String(50), nullable=True)  # 'one_time', 'annual', 'monthly'

    # Application details
    eligibility_criteria = Column(Text, nullable=False)
    eligibility_criteria_hi = Column(Text, nullable=True)
    application_process = Column(Text, nullable=False)
    application_process_hi = Column(Text, nullable=True)
    required_documents = Column(ARRAY(String), nullable=False)
    application_link = Column(String(1000), nullable=True)

    # Status and deadlines
    deadline_date = Column(Date, nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    state = Column(String(100), default='Jharkhand', nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<GovernmentScheme(code={self.scheme_code}, name={self.name}, category={self.category})>"

    def to_dict(self, language: str = 'en'):
        """Convert scheme to dictionary with language support"""
        is_hindi = language == 'hi'

        return {
            "id": str(self.id),
            "scheme_code": self.scheme_code,
            "name": self.name_hi if is_hindi and self.name_hi else self.name,
            "description": self.description_hi if is_hindi and self.description_hi else self.description,
            "category": self.category,
            "benefit_amount": float(self.benefit_amount) if self.benefit_amount else None,
            "benefit_frequency": self.benefit_frequency,
            "eligibility": self.eligibility_criteria_hi if is_hindi and self.eligibility_criteria_hi else self.eligibility_criteria,
            "application_process": self.application_process_hi if is_hindi and self.application_process_hi else self.application_process,
            "required_documents": self.required_documents or [],
            "application_link": self.application_link,
            "deadline": self.deadline_date.isoformat() if self.deadline_date else None,
            "implementing_agency": self.implementing_agency,
            "is_active": self.is_active,
            "state": self.state,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    @property
    def is_deadline_approaching(self):
        """Check if deadline is within 30 days"""
        if not self.deadline_date:
            return False
        from datetime import datetime, date
        days_until_deadline = (self.deadline_date - date.today()).days
        return 0 <= days_until_deadline <= 30

    @property
    def is_deadline_passed(self):
        """Check if deadline has passed"""
        if not self.deadline_date:
            return False
        from datetime import date
        return self.deadline_date < date.today()


class UserSchemeApplication(Base):
    """User scheme application tracking model"""

    __tablename__ = "user_scheme_applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    scheme_id = Column(UUID(as_uuid=True), ForeignKey("government_schemes.id", ondelete="CASCADE"), nullable=False)

    # Application details
    application_date = Column(Date, nullable=False)
    status = Column(String(50), default='applied', nullable=False, index=True)  # 'applied', 'approved', 'rejected', 'pending'
    notes = Column(Text, nullable=True)
    reminder_date = Column(Date, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="scheme_applications")
    scheme = relationship("GovernmentScheme", backref="user_applications")

    def __repr__(self):
        return f"<UserSchemeApplication(user_id={self.user_id}, scheme_id={self.scheme_id}, status={self.status})>"

    def to_dict(self):
        """Convert application to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "scheme_id": str(self.scheme_id),
            "application_date": self.application_date.isoformat() if self.application_date else None,
            "status": self.status,
            "notes": self.notes,
            "reminder_date": self.reminder_date.isoformat() if self.reminder_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "scheme": self.scheme.to_dict() if self.scheme else None
        }