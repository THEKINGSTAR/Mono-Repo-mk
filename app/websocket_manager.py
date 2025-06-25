from fastapi import WebSocket
from typing import Dict, List
import json

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)
    
    def disconnect(self, session_id: str, websocket: WebSocket = None):
        if session_id in self.active_connections:
            if websocket:
                self.active_connections[session_id].remove(websocket)
            else:
                self.active_connections[session_id] = []
    
    async def send_message(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    # Remove dead connections
                    self.active_connections[session_id].remove(connection)
