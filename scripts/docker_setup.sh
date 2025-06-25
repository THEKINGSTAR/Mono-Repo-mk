#!/bin/bash

echo "🐳 Setting up Docker environment for CambioML Backend"
echo "===================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Installing Docker..."
    
    # Install Docker (Ubuntu/Debian)
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    
    echo "✅ Docker installed. Please log out and log back in to use Docker without sudo."
    echo "   Then run this script again."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Installing..."
    
    # Install Docker Compose
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    echo "✅ Docker Compose installed."
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your ANTHROPIC_API_KEY"
    echo "   You can get an API key from: https://console.anthropic.com/"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p ssl
mkdir -p backups

# Pull required images
echo "📥 Pulling Docker images..."
docker-compose pull

# Build the application
echo "🏗️  Building application..."
docker-compose build

echo "✅ Docker setup completed!"
echo ""
echo "🚀 To start the services:"
echo "   docker-compose up -d"
echo ""
echo "🔧 To view logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 To stop services:"
echo "   docker-compose down"
