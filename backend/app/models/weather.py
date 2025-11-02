"""
Weather Model
Database model for weather data and forecasts
"""

import uuid
from sqlalchemy import Column, String, DateTime, Numeric, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class WeatherData(Base):
    """Weather data model for agricultural forecasting"""

    __tablename__ = "weather_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Location information
    location_name = Column(String(255), nullable=False, index=True)
    latitude = Column(Numeric(10, 8), nullable=False)
    longitude = Column(Numeric(11, 8), nullable=False)

    # Observation details
    observation_time = Column(DateTime(timezone=True), nullable=False, index=True)

    # Temperature data (Celsius)
    temperature_celsius = Column(Numeric(5, 2), nullable=False)
    feels_like_celsius = Column(Numeric(5, 2), nullable=True)

    # Humidity and rainfall
    humidity_percent = Column(Integer, nullable=False)
    rainfall_mm = Column(Numeric(5, 2), default=0, nullable=False)

    # Wind data
    wind_speed_kph = Column(Numeric(5, 2), nullable=True)

    # UV and conditions
    uv_index = Column(Integer, nullable=True)
    weather_condition = Column(String(255), nullable=False)
    weather_condition_hi = Column(String(255), nullable=True)

    # Source information
    source = Column(String(100), default='openweathermap', nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<WeatherData(location={self.location_name}, temp={self.temperature_celsius}°C, time={self.observation_time})>"

    def to_dict(self):
        """Convert weather data to dictionary"""
        return {
            "id": str(self.id),
            "location": {
                "name": self.location_name,
                "latitude": float(self.latitude),
                "longitude": float(self.longitude)
            },
            "observation_time": self.observation_time.isoformat() if self.observation_time else None,
            "temperature": {
                "current": float(self.temperature_celsius),
                "feels_like": float(self.feels_like_celsius) if self.feels_like_celsius else None,
                "unit": "celsius"
            },
            "humidity": self.humidity_percent,
            "rainfall": {
                "current": float(self.rainfall_mm),
                "unit": "mm"
            },
            "wind_speed": float(self.wind_speed_kph) if self.wind_speed_kph else None,
            "uv_index": self.uv_index,
            "conditions": {
                "en": self.weather_condition,
                "hi": self.weather_condition_hi
            },
            "source": self.source,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    @property
    def temperature_fahrenheit(self):
        """Convert temperature to Fahrenheit"""
        return (float(self.temperature_celsius) * 9/5) + 32 if self.temperature_celsius else None

    @property
    def is_rainy(self):
        """Check if weather indicates rain"""
        rainy_conditions = ['rain', 'drizzle', 'thunderstorm', 'showers']
        return any(condition in self.weather_condition.lower() for condition in rainy_conditions)

    @property
    def is_hot(self):
        """Check if weather is hot (above 35°C)"""
        return float(self.temperature_celsius) > 35 if self.temperature_celsius else False

    @property
    def is_cold(self):
        """Check if weather is cold (below 15°C)"""
        return float(self.temperature_celsius) < 15 if self.temperature_celsius else False

    @property
    def humidity_level(self):
        """Get humidity level description"""
        humidity = self.humidity_percent
        if humidity >= 80:
            return "very_high"
        elif humidity >= 60:
            return "high"
        elif humidity >= 40:
            return "moderate"
        elif humidity >= 20:
            return "low"
        else:
            return "very_low"