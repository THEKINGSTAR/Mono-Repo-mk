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

```
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
```

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
   ```bash
   git clone <your-repo-url>
   cd cambioml-backend
   ```

2. **Install dependencies**
   ```bash
   chmod +x scripts/install_deps.sh
   ./scripts/install_deps.sh
   source venv/bin/activate
   ```

3. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY
   ```

4. **Run the system**
   ```bash
   # Option 1: Full system with Docker
   docker-compose up --build

   # Option 2: Development mode
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access the application**
   - Frontend: http://localhost:8000/static/index.html
   - API Documentation: http://localhost:8000/docs
   - Interactive API: http://localhost:8000/redoc

### Quick Demo

Run the mock demo to see the system in action:

```bash
source venv/bin/activate
python scripts/simple_demo.py
```

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

```bash
curl -X POST "http://localhost:8000/sessions" \
     -H "Content-Type: application/json" \
     -d '{}'
```

Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "active",
  "vnc_url": "/vnc/550e8400-e29b-41d4-a716-446655440000",
  "websocket_url": "/ws/550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### WebSocket Endpoints

#### Real-time Agent Communication

Connect to: `ws://localhost:8000/ws/{session_id}`

**Send Message:**
```json
{
  "content": "Take a screenshot of the desktop"
}
```

**Receive Response:**
```json
{
  "type": "agent_response",
  "content": "I'll take a screenshot for you...",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### VNC Connection

Connect to: `ws://localhost:8000/vnc/{session_id}`

Provides WebSocket proxy for VNC connections to agent containers.

## 🗄️ Database Schema

### Sessions Table

```sql
CREATE TABLE sessions (
    id VARCHAR PRIMARY KEY,
    container_id VARCHAR NOT NULL,
    vnc_port INTEGER NOT NULL,
    status VARCHAR DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Chat Messages Table

```sql
CREATE TABLE chat_messages (
    id VARCHAR PRIMARY KEY,
    session_id VARCHAR NOT NULL,
    role VARCHAR NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON
);
```

## 🐳 Docker Configuration

### Services

- **backend**: FastAPI application server
- **postgres**: PostgreSQL database
- **redis**: Redis cache
- **agent-containers**: Dynamic containers for agent sessions

### Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=your_api_key_here

# Database
DATABASE_URL=postgresql://cambioml:password@postgres:5432/cambioml

# Redis
REDIS_URL=redis://redis:6379

# Optional
DEBUG=false
LOG_LEVEL=info
```

### Docker Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up --build -d

# Clean up volumes
docker-compose down -v
```

## 🔧 Development

### Project Structure

```
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
│   ├── install_deps.sh          # Dependency installation
│   ├── setup.sh                 # Full system setup
│   ├── simple_demo.py           # Mock demo
│   └── demo_script.py           # Full system demo
├── docker-compose.yml           # Docker services
├── Dockerfile                   # Application container
├── requirements.txt             # Python dependencies
└── .env.example                # Environment template
```

### Running in Development Mode

1. **Start database services**
   ```bash
   docker-compose up postgres redis -d
   ```

2. **Run FastAPI in development**
   ```bash
   source venv/bin/activate
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

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

```bash
# Unit tests
python -m pytest tests/unit/

# Integration tests
python -m pytest tests/integration/

# End-to-end tests
python -m pytest tests/e2e/

# All tests with coverage
python -m pytest --cov=app tests/
```

### Demo Scripts

```bash
# Mock demo (no backend required)
python scripts/simple_demo.py

# Full system demo
python scripts/demo_script.py

# Load testing
python scripts/load_test.py
```

## 📊 Monitoring and Logging

### Application Logs

```bash
# View application logs
docker-compose logs backend

# Follow logs in real-time
docker-compose logs -f backend

# Filter by log level
docker-compose logs backend | grep ERROR
```

### Database Monitoring

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U cambioml -d cambioml

# View active sessions
SELECT * FROM sessions WHERE status = 'active';

# View recent messages
SELECT * FROM chat_messages ORDER BY timestamp DESC LIMIT 10;
```

### Performance Metrics

- **Session Creation Time**: < 5 seconds
- **WebSocket Latency**: < 100ms
- **Container Startup**: < 10 seconds
- **Database Query Time**: < 50ms

## 🔒 Security Considerations

### Authentication

- API key validation for Anthropic services
- Session-based access control
- Container isolation

### Network Security

- Internal Docker network for services
- Exposed ports only for necessary services
- VNC password protection

### Data Protection

- Encrypted database connections
- Secure environment variable handling
- Container resource limits

## 🚀 Deployment

### Production Deployment

1. **Environment Setup**
   ```bash
   # Production environment variables
   export ANTHROPIC_API_KEY=your_production_key
   export DATABASE_URL=your_production_db_url
   export REDIS_URL=your_production_redis_url
   ```

2. **Docker Deployment**
   ```bash
   # Build production image
   docker build -t cambioml-backend:latest .

   # Deploy with docker-compose
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Kubernetes Deployment**
   ```bash
   # Apply Kubernetes manifests
   kubectl apply -f k8s/
   ```

### Scaling Considerations

- **Horizontal Scaling**: Multiple backend instances
- **Database Scaling**: Read replicas, connection pooling
- **Container Management**: Kubernetes for orchestration
- **Load Balancing**: Nginx or cloud load balancers

## 🐛 Troubleshooting

### Common Issues

1. **Container Creation Fails**
   ```bash
   # Check Docker daemon
   docker info
   
   # Check available resources
   docker system df
   ```

2. **Database Connection Issues**
   ```bash
   # Test database connection
   docker-compose exec postgres pg_isready
   
   # Check database logs
   docker-compose logs postgres
   ```

3. **WebSocket Connection Drops**
   ```bash
   # Check backend logs
   docker-compose logs backend | grep websocket
   
   # Test WebSocket endpoint
   wscat -c ws://localhost:8000/ws/test-session
   ```

4. **VNC Connection Problems**
   ```bash
   # Check VNC port availability
   netstat -tulpn | grep 590
   
   # Test VNC connection
   vncviewer localhost:5900
   ```

### Debug Mode

Enable debug logging:

```bash
export DEBUG=true
export LOG_LEVEL=debug
docker-compose up --build
```

## 📈 Performance Optimization

### Database Optimization

- Index frequently queried columns
- Use connection pooling
- Implement query caching
- Regular database maintenance

### Container Optimization

- Pre-built base images
- Resource limits and requests
- Container health checks
- Graceful shutdown handling

### WebSocket Optimization

- Connection pooling
- Message batching
- Compression for large messages
- Heartbeat mechanisms

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

```
feat: add new session management endpoint
fix: resolve WebSocket connection timeout
docs: update API documentation
test: add integration tests for container service
```

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
```
