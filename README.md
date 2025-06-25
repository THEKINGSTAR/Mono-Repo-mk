# CambioML Computer Use Agent Backend

A scalable FastAPI backend for managing Claude Computer Use agent sessions with real-time streaming and VNC integration.

## 🏗️ Architecture

This system replaces the original Streamlit interface with:
- **FastAPI Backend**: RESTful APIs + WebSocket streaming
- **Session Management**: Isolated Docker containers per session
- **Database Persistence**: PostgreSQL for chat history and session data
- **Real-time Communication**: WebSocket for agent streaming
- **VNC Integration**: Remote desktop access to agent environment

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Anthropic API key
- Python 3.11+ (for local development)

### 1. Clone and Setup
\`\`\`bash
git clone <your-repo-url>
cd cambioml-backend
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY
\`\`\`

### 2. Run with Docker Compose
\`\`\`bash
docker-compose up --build
\`\`\`

### 3. Access the Application
- Frontend: http://localhost:8000/static/index.html
- API Docs: http://localhost:8000/docs
- Database: localhost:5432

## 📡 API Endpoints

### REST API
- \`POST /sessions\` - Create new agent session
- \`GET /sessions/{session_id}\` - Get session details  
- \`DELETE /sessions/{session_id}\` - End session
- \`GET /sessions/{session_id}/history\` - Get chat history

### WebSocket
- \`/ws/{session_id}\` - Real-time agent communication

### Example Usage
\`\`\`javascript
// Create session
const response = await fetch('/sessions', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({})
});
const session = await response.json();

// Connect WebSocket
const ws = new WebSocket(\`ws://localhost:8000/ws/\${session.id}\`);
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Agent response:', data.content);
};

// Send message
ws.send(JSON.stringify({
  content: "Please open a web browser and navigate to google.com"
}));
\`\`\`

## 🏃‍♂️ Local Development

### Setup
\`\`\`bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install -r requirements.txt
\`\`\`

### Run Database
\`\`\`bash
docker-compose up postgres redis -d
\`\`\`

### Run Backend
\`\`\`bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
\`\`\`

## 🧪 Testing

### Manual Testing
1. Open http://localhost:8000/static/index.html
2. Wait for session creation and VNC connection
3. Send commands like:
   - "Take a screenshot"
   - "Open a web browser"
   - "Navigate to google.com and search for 'AI agents'"

### API Testing
\`\`\`bash
# Create session
curl -X POST http://localhost:8000/sessions

# Get session
curl http://localhost:8000/sessions/{session_id}

# Get chat history
curl http://localhost:8000/sessions/{session_id}/history
\`\`\`

## 🐳 Container Management

Each session runs in an isolated Docker container with:
- Ubuntu desktop environment
- VNC server (port 5900)
- noVNC web interface (port 6080)
- Claude computer use tools

Containers are automatically created and cleaned up with sessions.

## 📊 Database Schema

### Sessions Table
- \`id\`: UUID primary key
- \`container_id\`: Docker container ID
- \`vnc_port\`: VNC port number
- \`status\`: active/inactive/error
- \`created_at\`: Timestamp

### Chat Messages Table
- \`id\`: UUID primary key
- \`session_id\`: Foreign key to sessions
- \`role\`: user/assistant
- \`content\`: Message text
- \`timestamp\`: Message timestamp
- \`metadata\`: JSON metadata

## 🔧 Configuration

### Environment Variables
- \`ANTHROPIC_API_KEY\`: Your Anthropic API key
- \`DATABASE_URL\`: PostgreSQL connection string
- \`REDIS_URL\`: Redis connection string

### Docker Configuration
- Backend runs on port 8000
- PostgreSQL on port 5432
- Redis on port 6379
- VNC ports dynamically allocated (5900-6000 range)

## 🚀 Deployment

### Production Deployment
1. Set up a server with Docker
2. Configure environment variables
3. Run with docker-compose:
\`\`\`bash
docker-compose -f docker-compose.prod.yml up -d
\`\`\`

### Scaling Considerations
- Use Redis for session state sharing across instances
- Implement container orchestration (Kubernetes)
- Add load balancing for multiple backend instances
- Consider using managed databases (RDS, etc.)

## 🔍 Monitoring

### Health Checks
- \`GET /health\` - Backend health status
- Container monitoring via Docker API
- Database connection monitoring

### Logging
- Structured logging with timestamps
- WebSocket connection tracking
- Container lifecycle events
- Agent interaction logs

## 🛠️ Troubleshooting

### Common Issues
1. **Container creation fails**: Check Docker daemon and permissions
2. **VNC not connecting**: Verify port allocation and container status
3. **WebSocket disconnects**: Check network connectivity and session status
4. **Database connection errors**: Verify PostgreSQL is running and accessible

### Debug Mode
\`\`\`bash
# Run with debug logging
uvicorn app.main:app --reload --log-level debug
\`\`\`

## 📈 Performance

### Benchmarks
- Session creation: ~5-10 seconds
- WebSocket latency: <100ms
- Concurrent sessions: 10+ (depends on resources)
- Container overhead: ~500MB per session

### Optimization Tips
- Use container image caching
- Implement connection pooling
- Add Redis caching for frequent queries
- Monitor resource usage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
\`\`\`
