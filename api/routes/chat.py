"""POST /api/chat — text message to agent system."""

import uuid
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from api.services.agent_service import invoke_agent

router = APIRouter()


class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    language: str = "hi"


class ChatResponse(BaseModel):
    session_id: str
    response: str
    agent_activity: Optional[dict] = None
    merchant_id: Optional[str] = None


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())

    result = invoke_agent(session_id, req.message, language=req.language)

    return ChatResponse(
        session_id=session_id,
        response=result["response"],
        agent_activity=result.get("agent_activity"),
        merchant_id=result.get("merchant_id"),
    )
