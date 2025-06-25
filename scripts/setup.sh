#!/bin/bash

echo "🚀 Setting up CambioML Computer Use Agent Backend"
echo "================================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your ANTHROPIC_API_KEY"
    echo "   You can get an API key from: https://console.anthropic.com/"
    read -p "Press Enter after you've added your API key..."
fi

# Build and start services
echo "🏗️  Building and starting services..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Services are running!"
    echo ""
    echo "🌐 Access points:"
    echo "   Frontend: http://localhost:8000/static/index.html"
    echo "   API Docs: http://localhost:8000/docs"
    echo "   Database: localhost:5432"
    echo ""
    echo "🧪 Run demo:"
    echo "   python scripts/demo_script.py"
else
    echo "❌ Some services failed to start. Check logs with:"
    echo "   docker-compose logs"
fi
