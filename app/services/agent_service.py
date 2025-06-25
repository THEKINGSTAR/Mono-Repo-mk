import asyncio
import json
from typing import AsyncGenerator
from anthropic import Anthropic
import os
from ..database import get_db, ChatMessageDB
import uuid
from datetime import datetime

class AgentService:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
    async def process_message(self, user_message: str) -> AsyncGenerator[str, None]:
        """Process user message and stream agent response"""
        
        # Save user message to database
        await self._save_message("user", user_message)
        
        try:
            # Get chat history for context
            history = await self._get_chat_history()
            
            # Prepare messages for Claude
            messages = []
            for msg in history[-10:]:  # Last 10 messages for context
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Add current user message
            messages.append({
                "role": "user", 
                "content": user_message
            })
            
            # Stream response from Claude
            full_response = ""
            
            with self.client.messages.stream(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=messages,
                tools=[
                    {
                        "type": "computer_20241022",
                        "name": "computer",
                        "display_width_px": 1024,
                        "display_height_px": 768,
                        "display_number": 1,
                    }
                ],
            ) as stream:
                for text in stream.text_stream:
                    full_response += text
                    yield text
            
            # Save assistant response to database
            await self._save_message("assistant", full_response)
            
        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            yield error_msg
            await self._save_message("assistant", error_msg)
    
    async def _save_message(self, role: str, content: str):
        """Save message to database"""
        db = next(get_db())
        try:
            message = ChatMessageDB(
                id=str(uuid.uuid4()),
                session_id=self.session_id,
                role=role,
                content=content,
                timestamp=datetime.utcnow()
            )
            db.add(message)
            db.commit()
        finally:
            db.close()
    
    async def _get_chat_history(self):
        """Get chat history from database"""
        db = next(get_db())
        try:
            messages = db.query(ChatMessageDB).filter(
                ChatMessageDB.session_id == self.session_id
            ).order_by(ChatMessageDB.timestamp).all()
            
            return [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp
                }
                for msg in messages
            ]
        finally:
            db.close()
