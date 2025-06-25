from fastapi import FastAPI, WebSocket, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import asyncio
import uuid
from datetime import datetime
from typing import List, Optional
import json

from .database import get_db, SessionDB, ChatMessageDB
from .models import Session, ChatMessage, SessionCreate, SessionResponse
from .services import AgentService, ContainerService, VNCService
from .websocket_manager import WebSocketManager

app = FastAPI(title="CambioML Computer Use Backend", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

# Services
container_service = ContainerService()
vnc_service = VNCService()
websocket_manager = WebSocketManager()

@app.post("/sessions", response_model=SessionResponse)
async def create_session(
    session_data: SessionCreate,
    db = Depends(get_db)
):
    """Create a new agent session with isolated container"""
    try:
        # Create container for this session
        container_info = await container_service.create_container()
        
        # Create session in database
        session = SessionDB(
            id=str(uuid.uuid4()),
            container_id=container_info["container_id"],
            vnc_port=container_info["vnc_port"],
            status="active",
            created_at=datetime.utcnow()
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return SessionResponse(
            id=session.id,
            status=session.status,
            vnc_url=f"/vnc/{session.id}",
            websocket_url=f"/ws/{session.id}",
            created_at=session.created_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, db = Depends(get_db)):
    """Get session details"""
    session = db.query(SessionDB).filter(SessionDB.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return SessionResponse(
        id=session.id,
        status=session.status,
        vnc_url=f"/vnc/{session.id}",
        websocket_url=f"/ws/{session.id}",
        created_at=session.created_at
    )

@app.delete("/sessions/{session_id}")
async def end_session(session_id: str, db = Depends(get_db)):
    """End session and cleanup container"""
    session = db.query(SessionDB).filter(SessionDB.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Cleanup container
    await container_service.stop_container(session.container_id)
    
    # Update session status
    session.status = "inactive"
    db.commit()
    
    return {"message": "Session ended successfully"}

@app.get("/sessions/{session_id}/history")
async def get_chat_history(session_id: str, db = Depends(get_db)):
    """Get chat history for session"""
    messages = db.query(ChatMessageDB).filter(
        ChatMessageDB.session_id == session_id
    ).order_by(ChatMessageDB.timestamp).all()
    
    return [
        {
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.timestamp,
            "metadata": json.loads(msg.metadata) if msg.metadata else {}
        }
        for msg in messages
    ]

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time agent communication"""
    await websocket_manager.connect(websocket, session_id)
    
    try:
        # Initialize agent service for this session
        agent_service = AgentService(session_id)
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process message with agent
            async for response_chunk in agent_service.process_message(
                message_data["content"]
            ):
                await websocket_manager.send_message(
                    session_id, 
                    {
                        "type": "agent_response",
                        "content": response_chunk,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
                
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        websocket_manager.disconnect(session_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
