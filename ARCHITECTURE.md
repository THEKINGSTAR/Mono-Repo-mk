# System Architecture

## Overview
Replace Streamlit with FastAPI backend + WebSocket streaming + Database persistence

## Components

### 1. FastAPI Backend
- Session management APIs
- WebSocket endpoints for real-time streaming
- VNC proxy endpoints
- Chat history persistence

### 2. Database Layer
- PostgreSQL for session and chat history
- Redis for session state caching

### 3. Container Management
- Docker containers for isolated agent sessions
- VNC server in each container

### 4. Frontend
- Simple HTML/JS client
- WebSocket connection for real-time updates
- VNC viewer integration

## API Design

### REST Endpoints
- POST /sessions - Create new session
- GET /sessions/{session_id} - Get session details
- DELETE /sessions/{session_id} - End session
- GET /sessions/{session_id}/history - Get chat history

### WebSocket Endpoints
- /ws/{session_id} - Real-time agent communication
- /vnc/{session_id} - VNC streaming proxy

## Data Models

### Session
- id: UUID
- created_at: timestamp
- status: active/inactive/error
- container_id: string
- vnc_port: int

### ChatMessage
- id: UUID
- session_id: UUID
- role: user/assistant
- content: text
- timestamp: timestamp
- metadata: JSON
