#!/bin/bash

echo "🚀 CambioML Quick Start - Full System Demo"
echo "=========================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Creating from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your ANTHROPIC_API_KEY"
    exit 1
fi

# Check if API key is set
if ! grep -q "sk-ant-api03" .env; then
    echo "❌ ANTHROPIC_API_KEY not found in .env file"
    echo "   Please add your API key to the .env file"
    exit 1
fi

echo "✅ Environment configured with API key"

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Installing dependencies..."
    chmod +x scripts/install_deps.sh
    ./scripts/install_deps.sh
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Running mock demo instead..."
    source venv/bin/activate
    python scripts/simple_demo.py
    exit 0
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Running mock demo instead..."
    source venv/bin/activate
    python scripts/simple_demo.py
    exit 0
fi

# Start Docker services
echo "🐳 Starting Docker services..."
docker-compose down 2>/dev/null || true
docker-compose up --build -d

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 15

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ All services are running!"
    echo ""
    echo "🌐 Access Points:"
    echo "   • Frontend: http://localhost:8000/static/index.html"
    echo "   • API Docs: http://localhost:8000/docs"
    echo "   • Health Check: http://localhost:8000/health"
    echo ""
    echo "🧪 Testing the system..."
    
    # Test API endpoint
    sleep 5
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ Backend is responding"
        
        # Run full demo
        echo "🎬 Running full system demo..."
        source venv/bin/activate
        python scripts/demo_script.py
    else
        echo "⚠️  Backend not responding yet. You can:"
        echo "   • Check logs: docker-compose logs -f"
        echo "   • Try manual testing at: http://localhost:8000/static/index.html"
    fi
else
    echo "❌ Some services failed to start"
    echo "📋 Service status:"
    docker-compose ps
    echo ""
    echo "📋 Logs:"
    docker-compose logs --tail=20
    echo ""
    echo "🔧 You can still run the mock demo:"
    source venv/bin/activate
    python scripts/simple_demo.py
fi
