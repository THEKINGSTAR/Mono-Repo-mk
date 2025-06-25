# CambioML Computer Use Agent Backend - API Reference

Complete API documentation for the CambioML Computer Use Agent Backend.

## 🎯 Overview

The CambioML Backend provides RESTful APIs and WebSocket endpoints for managing Claude Computer Use agent sessions. This reference covers all available endpoints, request/response formats, and integration examples.

## 🔗 Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

## 🔐 Authentication

Currently, the API uses API key authentication for Anthropic services. Future versions will include user authentication.

## 📚 REST API Endpoints

### Sessions Management

#### Create Session

Creates a new agent session with an isolated container environment.

**Endpoint**: `POST /sessions`

**Request Body**:
\`\`\`json
{
  "name": "My Agent Session",
  "config": {
    "timeout": 3600,
    "max_messages": 100
  }
}
\`\`\`

**Response**:
\`\`\`json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "active",
  "vnc_url": "/vnc/550e8400-e29b-41d4-a716-446655440000",
  "websocket_url": "/ws/550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2024-01-15T10:30:00Z"
}
\`\`\`

**cURL Example**:
\`\`\`bash
curl -X POST "http://localhost:8000/sessions" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Test Session",
       "config": {"timeout": 1800}
     }'
\`\`\`

#### Get Session Details

Retrieves information about a specific session.

**Endpoint**: `GET /sessions/{session_id}`

**Response**:
\`\`\`json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "active",
  "vnc_url": "/vnc/550e8400-e29b-41d4-a716-446655440000",
  "websocket_url": "/ws/550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2024-01-15T10:30:00Z",
  "container_id": "docker-container-123",
  "vnc_port": 5900
}
\`\`\`

**cURL Example**:
\`\`\`bash
curl "http://localhost:8000/sessions/550e8400-e29b-41d4-a716-446655440000"
\`\`\`

#### List Sessions

Retrieves a list of all sessions.

**Endpoint**: `GET /sessions`

**Query Parameters**:
- `status` (optional): Filter by status (`active`, `inactive`, `error`)
- `limit` (optional): Number of results (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response**:
\`\`\`json
{
  "sessions": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "active",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
\`\`\`

**cURL Example**:
\`\`\`bash
curl "http://localhost:8000/sessions?status=active&limit=10"
\`\`\`

#### End Session

Terminates a session and cleans up associated resources.

**Endpoint**: `DELETE /sessions/{session_id}`

**Response**:
\`\`\`json
{
  "message": "Session ended successfully",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "ended_at": "2024-01-15T11:30:00Z"
}
\`\`\`

**cURL Example**:
\`\`\`bash
curl -X DELETE "http://localhost:8000/sessions/550e8400-e29b-41d4-a716-446655440000"
\`\`\`

### Chat History

#### Get Chat History

Retrieves the conversation history for a session.

**Endpoint**: `GET /sessions/{session_id}/history`

**Query Parameters**:
- `limit` (optional): Number of messages (default: 100)
- `offset` (optional): Pagination offset (default: 0)
- `role` (optional): Filter by role (`user`, `assistant`)

**Response**:
\`\`\`json
{
  "messages": [
    {
      "id": "msg-123",
      "role": "user",
      "content": "Take a screenshot",
      "timestamp": "2024-01-15T10:31:00Z",
      "metadata": {}
    },
    {
      "id": "msg-124",
      "role": "assistant",
      "content": "I'll take a screenshot for you...",
      "timestamp": "2024-01-15T10:31:05Z",
      "metadata": {
        "tool_calls": ["screenshot"]
      }
    }
  ],
  "total": 2,
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
\`\`\`

**cURL Example**:
\`\`\`bash
curl "http://localhost:8000/sessions/550e8400-e29b-41d4-a716-446655440000/history?limit=20"
\`\`\`

#### Clear Chat History

Clears the conversation history for a session.

**Endpoint**: `DELETE /sessions/{session_id}/history`

**Response**:
\`\`\`json
{
  "message": "Chat history cleared",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "cleared_messages": 15
}
\`\`\`

### System Endpoints

#### Health Check

Checks the health status of the backend services.

**Endpoint**: `GET /health`

**Response**:
\`\`\`json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "services": {
    "database": "up",
    "redis": "up",
    "docker": "up"
  },
  "version": "1.0.0"
}
\`\`\`

#### System Metrics

Provides system metrics (Prometheus format).

**Endpoint**: `GET /metrics`

**Response**: Prometheus metrics format
\`\`\`
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="/sessions"} 42
http_requests_total{method="POST",endpoint="/sessions"} 15
\`\`\`

## 🔌 WebSocket API

### Real-time Agent Communication

Connect to the WebSocket endpoint for real-time communication with the Claude agent.

**Endpoint**: `ws://localhost:8000/ws/{session_id}`

#### Connection

\`\`\`javascript
const ws = new WebSocket('ws://localhost:8000/ws/550e8400-e29b-41d4-a716-446655440000');

ws.onopen = function(event) {
    console.log('Connected to agent session');
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};

ws.onerror = function(error) {
    console.error('WebSocket error:', error);
};

ws.onclose = function(event) {
    console.log('Connection closed');
};
\`\`\`

#### Send Message

Send a message to the Claude agent:

\`\`\`javascript
const message = {
    content: "Take a screenshot of the desktop"
};

ws.send(JSON.stringify(message));
\`\`\`

#### Message Format

**Outgoing Message** (Client to Server):
\`\`\`json
{
  "content": "Your message to the agent",
  "metadata": {
    "timestamp": "2024-01-15T10:31:00Z"
  }
}
\`\`\`

**Incoming Message** (Server to Client):
\`\`\`json
{
  "type": "agent_response",
  "content": "Agent's response text",
  "timestamp": "2024-01-15T10:31:05Z",
  "metadata": {
    "tool_calls": ["screenshot"],
    "processing_time": 2.5
  }
}
\`\`\`

#### Message Types

1. **agent_response**: Standard agent text response
2. **tool_execution**: Tool execution status
3. **error**: Error messages
4. **status**: Session status updates
5. **heartbeat**: Connection keep-alive

**Tool Execution Message**:
\`\`\`json
{
  "type": "tool_execution",
  "tool": "screenshot",
  "status": "completed",
  "result": {
    "image_path": "/tmp/screenshot.png",
    "dimensions": "1920x1080"
  },
  "timestamp": "2024-01-15T10:31:03Z"
}
\`\`\`

**Error Message**:
\`\`\`json
{
  "type": "error",
  "error": "Tool execution failed",
  "details": "Screenshot tool not available",
  "timestamp": "2024-01-15T10:31:03Z"
}
\`\`\`

### VNC WebSocket

Connect to the VNC WebSocket for remote desktop access.

**Endpoint**: `ws://localhost:8000/vnc/{session_id}`

This endpoint provides a WebSocket proxy to the VNC server running in the agent's container.

## 📊 Response Codes

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 422 | Validation Error |
| 429 | Rate Limited |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

### Error Response Format

\`\`\`json
{
  "error": "Error type",
  "message": "Human readable error message",
  "details": {
    "field": "Additional error details"
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req-123456"
}
\`\`\`

## 🚦 Rate Limiting

The API implements rate limiting to prevent abuse:

- **General API**: 100 requests per minute per IP
- **Session Creation**: 10 sessions per minute per IP
- **WebSocket Connections**: 5 connections per minute per IP

Rate limit headers are included in responses:
\`\`\`
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248600
\`\`\`

## 📄 Pagination

List endpoints support pagination:

**Request**:
\`\`\`
GET /sessions?limit=20&offset=40
\`\`\`

**Response**:
\`\`\`json
{
  "data": [...],
  "pagination": {
    "limit": 20,
    "offset": 40,
    "total": 150,
    "has_next": true,
    "has_prev": true
  }
}
\`\`\`

## 🔍 Filtering and Sorting

### Filtering

Most list endpoints support filtering:

\`\`\`
GET /sessions?status=active&created_after=2024-01-01
GET /sessions/{id}/history?role=user&limit=50
\`\`\`

### Sorting

Use the `sort` parameter:

\`\`\`
GET /sessions?sort=created_at:desc
GET /sessions?sort=status:asc,created_at:desc
\`\`\`

## 🛠️ SDK Examples

### Python SDK

\`\`\`python
import asyncio
import aiohttp
import websockets
import json

class CambioMLClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        
    async def create_session(self, name=None, config=None):
        """Create a new agent session"""
        data = {}
        if name:
            data['name'] = name
        if config:
            data['config'] = config
            
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/sessions", json=data) as response:
                if response.status == 200:
                    self.session = await response.json()
                    return self.session
                else:
                    raise Exception(f"Failed to create session: {response.status}")
    
    async def send_message(self, message):
        """Send message via WebSocket"""
        if not self.session:
            raise Exception("No active session")
            
        uri = f"ws://localhost:8000/ws/{self.session['id']}"
        
        async with websockets.connect(uri) as websocket:
            await websocket.send(json.dumps({"content": message}))
            
            async for response in websocket:
                data = json.loads(response)
                if data['type'] == 'agent_response':
                    return data['content']
    
    async def get_history(self, limit=100):
        """Get chat history"""
        if not self.session:
            raise Exception("No active session")
            
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/sessions/{self.session['id']}/history"
            async with session.get(url, params={'limit': limit}) as response:
                return await response.json()
    
    async def end_session(self):
        """End the session"""
        if not self.session:
            return
            
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/sessions/{self.session['id']}"
            async with session.delete(url) as response:
                if response.status == 200:
                    self.session = None
                    return True
                return False

# Usage example
async def main():
    client = CambioMLClient()
    
    # Create session
    session = await client.create_session("My Test Session")
    print(f"Created session: {session['id']}")
    
    # Send message
    response = await client.send_message("Take a screenshot")
    print(f"Agent response: {response}")
    
    # Get history
    history = await client.get_history()
    print(f"Chat history: {len(history['messages'])} messages")
    
    # End session
    await client.end_session()
    print("Session ended")

if __name__ == "__main__":
    asyncio.run(main())
\`\`\`

### JavaScript SDK

\`\`\`javascript
class CambioMLClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
        this.session = null;
        this.websocket = null;
    }
    
    async createSession(name = null, config = null) {
        const data = {};
        if (name) data.name = name;
        if (config) data.config = config;
        
        const response = await fetch(`${this.baseUrl}/sessions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            this.session = await response.json();
            return this.session;
        } else {
            throw new Error(`Failed to create session: ${response.status}`);
        }
    }
    
    connectWebSocket() {
        if (!this.session) {
            throw new Error('No active session');
        }
        
        const wsUrl = `ws://localhost:8000/ws/${this.session.id}`;
        this.websocket = new WebSocket(wsUrl);
        
        return new Promise((resolve, reject) => {
            this.websocket.onopen = () => resolve(this.websocket);
            this.websocket.onerror = (error) => reject(error);
        });
    }
    
    async sendMessage(message) {
        if (!this.websocket) {
            await this.connectWebSocket();
        }
        
        this.websocket.send(JSON.stringify({
            content: message
        }));
    }
    
    onMessage(callback) {
        if (this.websocket) {
            this.websocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                callback(data);
            };
        }
    }
    
    async getHistory(limit = 100) {
        if (!this.session) {
            throw new Error('No active session');
        }
        
        const response = await fetch(
            `${this.baseUrl}/sessions/${this.session.id}/history?limit=${limit}`
        );
        
        if (response.ok) {
            return await response.json();
        } else {
            throw new Error(`Failed to get history: ${response.status}`);
        }
    }
    
    async endSession() {
        if (!this.session) return;
        
        const response = await fetch(`${this.baseUrl}/sessions/${this.session.id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            this.session = null;
            if (this.websocket) {
                this.websocket.close();
                this.websocket = null;
            }
            return true;
        }
        return false;
    }
}

// Usage
const client = new CambioMLClient();

async function demo() {
    // Create session
    const session = await client.createSession('My Session');
    console.log('Created session:', session.id);
    
    // Connect WebSocket
    await client.connectWebSocket();
    
    // Set up message handler
    client.onMessage((data) => {
        if (data.type === 'agent_response') {
            console.log('Agent:', data.content);
        }
    });
    
    // Send message
    await client.sendMessage('Take a screenshot');
    
    // Get history after some time
    setTimeout(async () => {
        const history = await client.getHistory();
        console.log('History:', history.messages.length, 'messages');
        
        // End session
        await client.endSession();
        console.log('Session ended');
    }, 5000);
}

demo().catch(console.error);
\`\`\`

This comprehensive API reference provides all the information needed to integrate with the CambioML Computer Use Agent Backend, including detailed examples and error handling patterns.
