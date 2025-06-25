from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class SessionCreate(BaseModel):
    name: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

class SessionResponse(BaseModel):
    id: str
    status: str
    vnc_url: str
    websocket_url: str
    created_at: datetime

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    metadata: Optional[Dict[str, Any]] = None

class Session(BaseModel):
    id: str
    container_id: str
    vnc_port: int
    status: str
    created_at: datetime
