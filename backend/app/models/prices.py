"""
Prices Models
Database models for crop prices and price alerts
"""

import uuid
from sqlalchemy import Column, String, DateTime, Numeric, Date, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class CropPrice(Base):
    """Crop price data model for market information"""

    __tablename__ = "crop_prices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Commodity information
    commodity_name = Column(String(255), nullable=False, index=True)
    commodity_name_hi = Column(String(255), nullable=True)
    variety = Column(String(255), nullable=True)
    grade = Column(String(50), nullable=True)

    # Market information
    market_name = Column(String(255), nullable=False, index=True)
    market_name_hi = Column(String(255), nullable=True)
    state = Column(String(100), default='Jharkhand', nullable=False)

    # Price information (in INR)
    min_price = Column(Numeric(10, 2), nullable=False)
    max_price = Column(Numeric(10, 2), nullable=False)
    modal_price = Column(Numeric(10, 2), nullable=False)
    price_unit = Column(String(50), default='Quintal', nullable=False)

    # Metadata
    arrival_date = Column(Date, nullable=False, index=True)
    source = Column(String(100), nullable=True)  # 'agmarknet', 'enam'
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<CropPrice(commodity={self.commodity_name}, market={self.market_name}, date={self.arrival_date})>"

    def to_dict(self):
        """Convert crop price to dictionary"""
        return {
            "id": str(self.id),
            "commodity": {
                "name": self.commodity_name,
                "name_hi": self.commodity_name_hi,
                "variety": self.variety,
                "grade": self.grade
            },
            "market": {
                "name": self.market_name,
                "name_hi": self.market_name_hi,
                "state": self.state
            },
            "prices": {
                "min_price": float(self.min_price),
                "max_price": float(self.max_price),
                "modal_price": float(self.modal_price),
                "unit": self.price_unit
            },
            "arrival_date": self.arrival_date.isoformat() if self.arrival_date else None,
            "source": self.source,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class PriceAlert(Base):
    """Price alert model for user notifications"""

    __tablename__ = "price_alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Alert configuration
    commodity_name = Column(String(255), nullable=False, index=True)
    market_name = Column(String(255), nullable=False)
    alert_type = Column(String(20), nullable=False)  # 'above', 'below', 'change_percent'
    threshold_value = Column(Numeric(10, 2), nullable=False)
    change_percentage = Column(Numeric(5, 2), nullable=True)  # For percentage-based alerts

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="price_alerts")

    def __repr__(self):
        return f"<PriceAlert(user_id={self.user_id}, commodity={self.commodity_name}, type={self.alert_type})>"

    def to_dict(self):
        """Convert price alert to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "commodity_name": self.commodity_name,
            "market_name": self.market_name,
            "alert_type": self.alert_type,
            "threshold_value": float(self.threshold_value),
            "change_percentage": float(self.change_percentage) if self.change_percentage else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }