"""
Chat Models
Database models for AI chatbot conversations and interactions
"""

import uuid
from sqlalchemy import Column, String, DateTime, Integer, Text, ARRAY, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ChatConversation(Base):
    """Chat conversation model for storing AI assistant interactions"""

    __tablename__ = "chat_conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(String(255), nullable=False, index=True)
    language = Column(String(2), nullable=False)  # 'en' or 'hi'

    # Conversation content
    message = Column(Text, nullable=False)  # User message
    response = Column(Text, nullable=False)  # Bot response
    context_tags = Column(ARRAY(String), nullable=True)  # ['crop_disease', 'pest_management']

    # Metadata
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    response_time_ms = Column(Integer, nullable=True)  # Performance monitoring
    user_feedback = Column(Integer, nullable=True)  # 1-5 rating

    # Relationships
    user = relationship("User", backref="chat_conversations")

    def __repr__(self):
        return f"<ChatConversation(id={self.id}, user_id={self.user_id}, session={self.session_id})>"

    def to_dict(self):
        """Convert chat conversation to dictionary"""
        return {
            "conversation_id": str(self.id),
            "session_id": self.session_id,
            "user_message": self.message,
            "bot_response": self.response,
            "language": self.language,
            "context_tags": self.context_tags or [],
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "response_time_ms": self.response_time_ms,
            "user_feedback": self.user_feedback
        }