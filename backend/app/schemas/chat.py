"""
Chat Schemas
Pydantic models for chatbot API requests and responses
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ChatRequest(BaseModel):
    """Chat request model for user messages"""
    message: str = Field(..., min_length=1, max_length=1000, description="User message text")
    language: str = Field(default="en", regex="^(en|hi)$", description="Language code: en or hi")
    session_id: Optional[str] = Field(None, description="Session identifier for conversation context")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "मेरी धान की फसल को कीड़ा लग गया है, क्या करें?",
                "language": "hi",
                "session_id": "session_12345"
            }
        }


class ChatResponse(BaseModel):
    """Chat response model for bot replies"""
    response: str = Field(..., description="Bot response text")
    language: str = Field(..., description="Response language code")
    timestamp: datetime = Field(..., description="Response timestamp")
    session_id: str = Field(..., description="Session identifier")
    context_tags: List[str] = Field(default=[], description="Agricultural context tags")
    response_time_ms: Optional[int] = Field(None, description="Response generation time in milliseconds")

    class Config:
        json_schema_extra = {
            "example": {
                "response": "आपकी धान की फसल के लिए कुछ सुझाव: 1. नीम तेल का छिड़काव करें 2. प्रभावित पौधों को हटाएं 3. कृषि विशेषज्ञ से सलाह लें",
                "language": "hi",
                "timestamp": "2024-01-01T12:00:00Z",
                "session_id": "session_12345",
                "context_tags": ["crop_disease", "pest_management", "paddy"],
                "response_time_ms": 1500
            }
        }


class ChatHistory(BaseModel):
    """Chat history model for conversation retrieval"""
    session_id: str = Field(..., description="Session identifier")
    messages: List[dict] = Field(..., description="List of conversation messages")
    total_messages: int = Field(..., description="Total number of messages")
    language: str = Field(..., description="Conversation language")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session_12345",
                "messages": [
                    {
                        "conversation_id": "uuid-123",
                        "user_message": "मेरी धान की फसल को कीड़ा लग गया है",
                        "bot_response": "आपकी धान की फसल के लिए कुछ सुझाव...",
                        "timestamp": "2024-01-01T12:00:00Z",
                        "context_tags": ["crop_disease"]
                    }
                ],
                "total_messages": 5,
                "language": "hi"
            }
        }


class QuickQuestion(BaseModel):
    """Quick question suggestions for chatbot"""
    question: str = Field(..., description="Suggested question text")
    category: str = Field(..., description="Question category")
    language: str = Field(..., description="Question language")

    class Config:
        json_schema_extra = {
            "example": {
                "question": "धान की बीमारी का इलाज क्या है?",
                "category": "crop_disease",
                "language": "hi"
            }
        }