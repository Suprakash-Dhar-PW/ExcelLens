from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from core.database import get_db
from models.database import CopilotSession, CopilotMessage
from services.gemini_service import GeminiService
import uuid

router = APIRouter()

class ChatRequest(BaseModel):
    session_id: str = None
    message: str

class ChatResponse(BaseModel):
    session_id: str
    reply: str

@router.post("/chat", response_model=ChatResponse)
def chat_with_copilot(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        # Get or create session
        if request.session_id:
            session_id = uuid.UUID(request.session_id)
            session = db.query(CopilotSession).filter(CopilotSession.id == session_id).first()
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
        else:
            session = CopilotSession()
            db.add(session)
            db.commit()
            db.refresh(session)
            session_id = session.id
            
        # Store user message
        user_msg = CopilotMessage(session_id=session.id, sender="user", message=request.message)
        db.add(user_msg)
        db.commit()
        
        # Get history
        history = db.query(CopilotMessage).filter(CopilotMessage.session_id == session.id).order_by(CopilotMessage.timestamp).all()
        messages_for_ai = [{"sender": m.sender, "message": m.message} for m in history]
        
        # Generate AI response
        from services.analytics_service import AnalyticsService
        import json
        
        # Get data context
        data_context = AnalyticsService.get_full_context(db)
        gemini = GeminiService()
        
        system_prompt = (
            "You are a Revenue Command Center AI Copilot. You assist users with analyzing their sales and revenue data. "
            "Use the following data context from their database to provide grounded, factual, and concise answers.\n\n"
            f"Context:\n{json.dumps(data_context, indent=2)}"
        )
        reply_text = gemini.generate_chat_response(messages_for_ai, system_instruction=system_prompt)
        
        # Store AI response
        ai_msg = CopilotMessage(session_id=session.id, sender="ai", message=reply_text)
        db.add(ai_msg)
        db.commit()
        
        return ChatResponse(session_id=str(session.id), reply=reply_text)
    except Exception as e:
        import logging
        logging.error(f"Copilot Chat Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
