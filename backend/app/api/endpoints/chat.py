"""
Chat API Endpoints
AI chatbot functionality with agricultural knowledge
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Optional, List
import asyncio
import uuid
from datetime import datetime

from app.schemas.chat import ChatRequest, ChatResponse, ChatHistory
from app.core.database import get_async_db
from app.models.chat import ChatConversation
from app.models.user import User
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

router = APIRouter()


# Mock responses for demonstration (replace with actual LLM integration)
MOCK_RESPONSES = {
    'en': {
        'fertilizer': [
            "For paddy crop, I recommend using 50-60 kg/acre of urea, 25-30 kg/acre of DAP, and 20-25 kg/acre of Muriate of Potash. Apply in split doses for better results.",
            "For wheat, use 60-70 kg/acre of urea, 30-35 kg/acre of DAP, and 15-20 kg/acre of potash. Apply half dose at sowing and half after 25-30 days.",
            "For maize, apply 80-100 kg/acre of urea, 40-50 kg/acre of DAP, and 30-40 kg/acre of potash. Apply in 3 split doses."
        ],
        'pest': [
            "For pest control in paddy, use neem oil spray (5%) or install pheromone traps. Chemical options include chlorantraniliprole or flubendiamide.",
            "For wheat pests like aphids, use imidacloprid or thiamethoxam as seed treatment. For foliar application, use lambda-cyhalothrin.",
            "For maize pests, apply appropriate insecticides based on the specific pest. Always follow recommended dosage and safety guidelines."
        ],
        'weather': [
            "Today's weather is good for farming activities. Temperature is around 28°C with moderate humidity. No rainfall expected.",
            "Current weather conditions are favorable for most crops. Adequate sunshine and moderate temperatures will help in crop growth.",
            "Weather conditions are normal for this season. Plan your irrigation and farming activities accordingly."
        ],
        'general': [
            "I'm here to help you with farming advice. Feel free to ask about crops, weather, pest control, or government schemes.",
            "Thank you for your question. Based on current agricultural practices, I recommend following proper farming methods.",
            "That's a good question about farming. Always consult with local agricultural experts for specific advice."
        ]
    },
    'hi': {
        'fertilizer': [
            "धान की फसल के लिए, मैं 50-60 किग्रा/एकड़ यूरिया, 25-30 किग्रा/एकड़ डीएपी, और 20-25 किग्रा/एकड़ म्यूरिएट ऑफ पोटाश की सिफारिश करता हूं। बेहतर परिणामों के लिए विभाजित खुराक में लागू करें।",
            "गेहूं के लिए, 60-70 किग्रा/एकड़ यूरिया, 30-35 किग्रा/एकड़ डीएपी, और 15-20 किग्रा/एकड़ पोटाश का उपयोग करें। बोने पर आधा खुराक और 25-30 दिनों के बाद आधा लगाएं।",
            "मक्का के लिए, 80-100 किग्रा/एकड़ यूरिया, 40-50 किग्रा/एकड़ डीएपी, और 30-40 किग्रा/एकड़ पोटाश लागू करें। 3 विभाजित खुराक में लागू करें।"
        ],
        'pest': [
            "धान में कीट नियंत्रण के लिए, नीम तेल का छिड़काव (5%) लगाएं या फेरोमोन जाल लगाएं। रासायनिक विकल्पों में क्लोरान्ट्रानिलिप्रोल या फ्लुबेंडियामाइड शामिल हैं।",
            "गेहूं के कीटों जैसे एफिड्स के लिए, बीज उपचार के रूप में इमिडाक्लोप्रिड या थियामेथॉक्सैम का उपयोग करें। पत्ते पर लगाने के लिए, लैम्डा-साइहलोथ्रिन का उपयोग करें।",
            "मक्का के कीटों के लिए, विशिष्ट कीट के आधार पर उपयुक्त कीटनाशक लागू करें। हमेशा अनुशंसित खुराक और सुरक्षा दिशानिर्देशियों का पालन करें।"
        ],
        'weather': [
            "आज का मौसम खेती गतिविधियों के लिए अच्छा है। तापमान लगभग 28°C है और मध्यम आर्द्रता है। वर्षा की उम्मीद नहीं है।",
            "वर्तमान मौसम की स्थितियां अधिकांश फसलों के लिए अनुकूल हैं। पर्याप्त धूप और मध्यम तापमान फसल वृद्धि में मदद करेंगे।",
            "मौसम की स्थितियां इस मौसम के लिए सामान्य हैं। अपनी सिंचाई और खेती गतिविधियों की तदनुसार योजना बनाएं।"
        ],
        'general': [
            "मैं आपको खेती सलाह में मदद करने के लिए यहां हूं। फसलों, मौसम, कीट नियंत्रण, या सरकारी योजनाओं के बारे में पूछने के लिए स्वतंत्र महसूस करें।",
            "आपके प्रश्न के लिए धन्यवाद।। वर्तमान कृषि प्रथाओं के आधार पर, मैं उचित खेती तरीकों का पालन करने की सलाह देता हूं।",
            "खेती के बारे में यह एक अच्छा प्रश्न है। विशिष्ट सलाह के लिए हमेशा स्थानीय कृषि विशेषज्ञों से परामर्श करें।"
        ]
    }
}


def get_mock_response(message: str, language: str = 'en') -> str:
    """Get mock response based on message content and language"""
    message_lower = message.lower()

    # Keywords for different categories
    if any(word in message_lower for word in ['fertilizer', 'उर्वरक', 'urea', 'dap', 'nutrient', 'पोषक']):
        responses = MOCK_RESPONSES[language]['fertilizer']
    elif any(word in message_lower for word in ['pest', 'कीट', 'insect', 'disease', 'बीमारी', 'control', 'नियंत्रण']):
        responses = MOCK_RESPONSES[language]['pest']
    elif any(word in message_lower for word in ['weather', 'मौसम', 'rain', 'वर्षा', 'temperature', 'तापमान']):
        responses = MOCK_RESPONSES[language]['weather']
    else:
        responses = MOCK_RESPONSES[language]['general']

    import random
    return random.choice(responses)


def extract_context_tags(message: str) -> List[str]:
    """Extract context tags from message"""
    message_lower = message.lower()
    tags = []

    if any(word in message_lower for word in ['fertilizer', 'उर्वरक', 'nutrient', 'पोषक']):
        tags.append('fertilizer')
    if any(word in message_lower for word in ['pest', 'कीट', 'insect', 'disease', 'बीमारी']):
        tags.append('pest_management')
    if any(word in message_lower for word in ['weather', 'मौसम', 'rain', 'वर्षा']):
        tags.append('weather')
    if any(word in message_lower for word in ['scheme', 'योजना', 'government', 'सरकार', 'benefit', 'लाभ']):
        tags.append('government_schemes')
    if any(word in message_lower for word in ['price', 'दाम', 'market', 'मंडी', 'sell', 'बेच']):
        tags.append('market_prices')

    return tags[:3]  # Return max 3 tags


@router.post("/", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    db: Session = Depends(get_async_db)
):
    """Send a message to the AI assistant"""
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())

        # Get mock response (replace with actual LLM integration)
        response_text = get_mock_response(request.message, request.language)
        context_tags = extract_context_tags(request.message)

        # Save conversation to database
        chat_conversation = ChatConversation(
            session_id=session_id,
            language=request.language,
            message=request.message,
            response=response_text,
            context_tags=context_tags,
            response_time_ms=1500  # Mock response time
        )

        db.add(chat_conversation)
        db.commit()
        db.refresh(chat_conversation)

        return ChatResponse(
            response=response_text,
            language=request.language,
            timestamp=datetime.now(),
            session_id=session_id,
            context_tags=context_tags,
            response_time_ms=1500
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")


@router.get("/history/{session_id}", response_model=ChatHistory)
async def get_chat_history(
    session_id: str,
    db: Session = Depends(get_async_db)
):
    """Get conversation history for a session"""
    try:
        # Query conversations from database
        result = db.execute(
            select(ChatConversation)
            .where(ChatConversation.session_id == session_id)
            .order_by(desc(ChatConversation.timestamp))
            .limit(50)
        )

        conversations = result.scalars().all()

        # Convert to response format
        messages = []
        for conv in conversations:
            messages.append({
                "conversation_id": str(conv.id),
                "user_message": conv.message,
                "bot_response": conv.response,
                "timestamp": conv.timestamp.isoformat(),
                "context_tags": conv.context_tags or []
            })

        return ChatHistory(
            session_id=session_id,
            messages=list(reversed(messages)),  # Reverse to show chronological order
            total_messages=len(messages),
            language=conversations[0].language if conversations else 'en'
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch chat history: {str(e)}")


@router.delete("/history/{session_id}")
async def clear_chat_history(
    session_id: str,
    db: Session = Depends(get_async_db)
):
    """Clear chat history for a session"""
    try:
        # Delete conversations from database
        result = db.execute(
            select(ChatConversation).where(ChatConversation.session_id == session_id)
        )

        conversations = result.scalars().all()
        for conv in conversations:
            db.delete(conv)

        db.commit()

        return {"message": f"Chat history cleared for session {session_id}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear chat history: {str(e)}")


@router.get("/sessions")
async def get_user_sessions(
    user_id: Optional[str] = None,
    db: Session = Depends(get_async_db)
):
    """Get list of chat sessions for a user"""
    try:
        # For now, return recent unique session IDs
        # In production, this would be filtered by user_id
        result = db.execute(
            select(ChatConversation.session_id, ChatConversation.timestamp)
            .distinct()
            .order_by(desc(ChatConversation.timestamp))
            .limit(10)
        )

        sessions = result.all()

        return {
            "sessions": [
                {
                    "session_id": session.session_id,
                    "last_message_time": session.timestamp.isoformat()
                }
                for session in sessions
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch sessions: {str(e)}")


@router.post("/feedback")
async def submit_feedback(
    conversation_id: str,
    feedback: int,
    db: Session = Depends(get_async_db)
):
    """Submit feedback for a conversation response"""
    try:
        if feedback < 1 or feedback > 5:
            raise HTTPException(status_code=400, detail="Feedback must be between 1 and 5")

        # Find and update conversation
        result = db.execute(
            select(ChatConversation).where(ChatConversation.id == conversation_id)
        )

        conversation = result.scalar_one_or_none()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        conversation.user_feedback = feedback
        db.commit()

        return {"message": "Feedback submitted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")


@router.get("/health")
async def chat_health():
    """Health check for chat service"""
    return {
        "status": "healthy",
        "service": "chat",
        "message": "AI chat service is running"
    }