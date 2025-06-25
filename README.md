# CambioML Computer Use Agent Backend

A scalable backend system for managing Claude Computer Use agent sessions with real-time streaming, VNC integration, and persistent chat history.

## 🎯 Overview

This project replaces the experimental Streamlit interface from Anthropic's computer-use-demo with a production-ready FastAPI backend that provides:

- **Session Management**: Create and manage isolated agent sessions
- **Real-time Streaming**: WebSocket-based communication with Claude agents
- **VNC Integration**: Remote desktop access to agent environments
- **Database Persistence**: Chat history and session data storage
- **Docker Containerization**: Easy deployment and scaling
- **RESTful APIs**: Clean, documented API endpoints

## 🏗️ Architecture

\`\`\`
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   PostgreSQL    │
│   (HTML/JS)     │◄──►│   Backend       │◄──►│   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   WebSocket     │    │   Docker        │    │   Redis         │
│   Streaming     │    │   Containers    │    │   Cache         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   VNC Server    │
                       │   (Remote       │
                       │   Desktop)      │
                       └─────────────────┘
\`\`\`

### Core Components

1. **FastAPI Backend** (`app/`)
   - REST API endpoints for session management
   - WebSocket endpoints for real-time communication
   - Database models and services
   - Container orchestration

2. **Database Layer**
   - PostgreSQL for persistent data storage
   - Redis for session state caching
   - SQLAlchemy ORM for database operations

3. **Container Management**
   - Docker containers for isolated agent sessions
   - VNC servers for remote desktop access
   - Automatic cleanup and resource management

4. **Frontend Interface**
   - Simple HTML/JavaScript client
   - Real-time chat interface
   - Integrated VNC viewer

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Anthropic API key

### Installation

1. **Clone the repository**
   \`\`\`bash
   git clone <your-repo-url>
   cd cambioml-backend
   \`\`\`

2. **Set up environment securely**
   \`\`\`bash
   chmod +x scripts/setup_env.sh
   ./scripts/setup_env.sh
   # Edit .env and add your ANTHROPIC_API_KEY
   \`\`\`

3. **Install dependencies**
   \`\`\`bash
   chmod +x scripts/install_deps.sh
   ./scripts/install_deps.sh
   source venv/bin/activate
   \`\`\`

4. **Run security check**
   \`\`\`bash
   chmod +x scripts/security_check.sh
   ./scripts/security_check.sh
   \`\`\`

5. **Start the system**
   \`\`\`bash
   # Quick start (recommended)
   chmod +x scripts/quick_start.sh
   ./scripts/quick_start.sh

   # Or manual Docker setup
   docker-compose up --build -d
   \`\`\`

6. **Access the application**
   - Frontend: http://localhost:8000/static/index.html
   - API Documentation: http://localhost:8000/docs
   - Interactive API: http://localhost:8000/redoc

### Quick Demo

Run the mock demo to see the system in action:

\`\`\`bash
source venv/bin/activate
python scripts/simple_demo.py
\`\`\`

## 📚 API Documentation

### REST Endpoints

#### Sessions

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/sessions` | Create a new agent session |
| GET | `/sessions/{session_id}` | Get session details |
| DELETE | `/sessions/{session_id}` | End session and cleanup |
| GET | `/sessions/{session_id}/history` | Get chat history |

#### Session Creation

\`\`\`bash
curl -X POST "http://localhost:8000/sessions" \
     -H "Content-Type: application/json" \
     -d '{}'
\`\`\`

Response:
\`\`\`json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "active",
  "vnc_url": "/vnc/550e8400-e29b-41d4-a716-446655440000",
  "websocket_url": "/ws/550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2024-01-15T10:30:00Z"
}
\`\`\`

### WebSocket Endpoints

#### Real-time Agent Communication

Connect to: `ws://localhost:8000/ws/{session_id}`

**Send Message:**
\`\`\`json
{
  "content": "Take a screenshot of the desktop"
}
\`\`\`

**Receive Response:**
\`\`\`json
{
  "type": "agent_response",
  "content": "I'll take a screenshot for you...",
  "timestamp": "2024-01-15T10:30:00Z"
}
\`\`\`

#### VNC Connection

Connect to: `ws://localhost:8000/vnc/{session_id}`

Provides WebSocket proxy for VNC connections to agent containers.

## 🗄️ Database Schema

### Sessions Table

\`\`\`sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    container_id VARCHAR(255) NOT NULL,
    vnc_port INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);
\`\`\`

### Chat Messages Table

\`\`\`sql
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);
\`\`\`

## 🐳 Docker Configuration

### Services

- **backend**: FastAPI application server
- **postgres**: PostgreSQL database
- **redis**: Redis cache
- **agent-containers**: Dynamic containers for agent sessions

### Environment Variables

\`\`\`bash
# Required
ANTHROPIC_API_KEY=your_api_key_here

# Database
DATABASE_URL=postgresql://cambioml:password@postgres:5432/cambioml

# Redis
REDIS_URL=redis://redis:6379

# Optional
DEBUG=false
LOG_LEVEL=info
\`\`\`

### Docker Commands

\`\`\`bash
# Use the management script (recommended)
./scripts/docker_commands.sh start    # Start all services
./scripts/docker_commands.sh stop     # Stop all services
./scripts/docker_commands.sh logs     # View logs
./scripts/docker_commands.sh status   # Check status

# Or use docker-compose directly
docker-compose up -d              # Start services
docker-compose logs -f            # View logs
docker-compose down               # Stop services
docker-compose up --build -d      # Rebuild and restart
\`\`\`

## 🔧 Development

### Project Structure

\`\`\`
cambioml-backend/
├── app/                          # FastAPI application
│   ├── main.py                   # Application entry point
│   ├── models.py                 # Pydantic models
│   ├── database.py               # Database configuration
│   ├── websocket_manager.py      # WebSocket management
│   └── services/                 # Business logic
│       ├── agent_service.py      # Claude agent integration
│       ├── container_service.py  # Docker container management
│       └── vnc_service.py        # VNC proxy service
├── static/                       # Frontend files
│   └── index.html               # Web interface
├── scripts/                      # Utility scripts
│   ├── setup_env.sh             # Secure environment setup
│   ├── install_deps.sh          # Dependency installation
│   ├── quick_start.sh           # Complete system startup
│   ├── security_check.sh        # Security validation
│   ├── simple_demo.py           # Mock demo
│   └── demo_script.py           # Full system demo
├── docker-compose.yml           # Docker services
├── docker-compose.prod.yml      # Production configuration
├── Dockerfile                   # Application container
├── Dockerfile.prod              # Production container
├── requirements.txt             # Python dependencies
├── .env.example                # Environment template
└── .gitignore                  # Git ignore rules
\`\`\`

### Running in Development Mode

1. **Start database services**
   \`\`\`bash
   docker-compose up postgres redis -d
   \`\`\`

2. **Run FastAPI in development**
   \`\`\`bash
   source venv/bin/activate
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   \`\`\`

3. **Access development tools**
   - Auto-reload on code changes
   - Interactive API docs at `/docs`
   - Database admin tools

### Adding New Features

1. **API Endpoints**: Add to `app/main.py`
2. **Database Models**: Update `app/database.py`
3. **Business Logic**: Create services in `app/services/`
4. **Frontend**: Modify `static/index.html`
5. **Tests**: Add to `tests/` directory

## 🧪 Testing

### Running Tests

\`\`\`bash
# Unit tests
python -m pytest tests/unit/

# Integration tests
python -m pytest tests/integration/

# End-to-end tests
python -m pytest tests/e2e/

# All tests with coverage
python -m pytest --cov=app tests/
\`\`\`

### Demo Scripts

\`\`\`bash
# Mock demo (no backend required)
python scripts/simple_demo.py

# Full system demo
python scripts/demo_script.py

# API key test
python scripts/test_api_key.py
\`\`\`

## 📊 Monitoring and Logging

### Application Logs

\`\`\`bash
# View application logs
docker-compose logs backend

# Follow logs in real-time
docker-compose logs -f backend

# Filter by log level
docker-compose logs backend | grep ERROR
\`\`\`

### Database Monitoring

\`\`\`bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U cambioml -d cambioml

# View active sessions
SELECT * FROM sessions WHERE status = 'active';

# View recent messages
SELECT * FROM chat_messages ORDER BY timestamp DESC LIMIT 10;
\`\`\`

### Performance Metrics

- **Session Creation Time**: < 5 seconds
- **WebSocket Latency**: < 100ms
- **Container Startup**: < 10 seconds
- **Database Query Time**: < 50ms

## 🔒 Security

### Security Features

- Environment variable isolation
- Git history protection
- API key validation
- Container isolation
- Network security

### Security Scripts

\`\`\`bash
# Set up secure environment
./scripts/setup_env.sh

# Run security check
./scripts/security_check.sh

# Clean git history (if needed)
./scripts/clean_git_history.sh
\`\`\`

### Best Practices

- Never commit `.env` files
- Use different API keys for dev/staging/prod
- Rotate API keys regularly
- Monitor API key usage
- Use HTTPS in production

## 🚀 Deployment

### Production Deployment

1. **Environment Setup**
   \`\`\`bash
   # Production environment variables
   export ANTHROPIC_API_KEY=your_production_key
   export DATABASE_URL=your_production_db_url
   export REDIS_URL=your_production_redis_url
   \`\`\`

2. **Docker Deployment**
   \`\`\`bash
   # Build production image
   docker build -f Dockerfile.prod -t cambioml-backend:latest .

   # Deploy with production compose
   docker-compose -f docker-compose.prod.yml up -d
   \`\`\`

3. **Kubernetes Deployment**
   \`\`\`bash
   # Apply Kubernetes manifests
   kubectl apply -f k8s/
   \`\`\`

### Scaling Considerations

- **Horizontal Scaling**: Multiple backend instances
- **Database Scaling**: Read replicas, connection pooling
- **Container Management**: Kubernetes for orchestration
- **Load Balancing**: Nginx or cloud load balancers

## 🐛 Troubleshooting

### Common Issues

1. **Container Creation Fails**
   \`\`\`bash
   # Check Docker daemon
   docker info
   
   # Check available resources
   docker system df
   \`\`\`

2. **Database Connection Issues**
   \`\`\`bash
   # Test database connection
   docker-compose exec postgres pg_isready
   
   # Check database logs
   docker-compose logs postgres
   \`\`\`

3. **WebSocket Connection Drops**
   \`\`\`bash
   # Check backend logs
   docker-compose logs backend | grep websocket
   
   # Test WebSocket endpoint
   wscat -c ws://localhost:8000/ws/test-session
   \`\`\`

4. **API Key Issues**
   \`\`\`bash
   # Test API key
   python scripts/test_api_key.py
   
   # Check environment
   ./scripts/security_check.sh
   \`\`\`

### Debug Mode

Enable debug logging:

\`\`\`bash
export DEBUG=true
export LOG_LEVEL=debug
docker-compose up --build
\`\`\`

## 🤝 Contributing

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

### Code Standards

- Follow PEP 8 for Python code
- Use type hints
- Write comprehensive docstrings
- Add unit tests for new features
- Update documentation

### Commit Guidelines

\`\`\`
feat: add new session management endpoint
fix: resolve WebSocket connection timeout
docs: update API documentation
test: add integration tests for container service
\`\`\`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Anthropic](https://anthropic.com) for the Claude Computer Use capabilities
- [FastAPI](https://fastapi.tiangolo.com) for the excellent web framework
- [Docker](https://docker.com) for containerization technology

## 📞 Support

For questions, issues, or contributions:

- Create an issue on GitHub
- Check the troubleshooting section
- Review the API documentation
- Run the demo scripts for examples

---

**Built for the CambioML Founding Backend Engineer Challenge**

*Demonstrating scalable backend architecture for AI agent session management*
