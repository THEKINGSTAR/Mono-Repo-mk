#!/bin/bash

echo "🔧 Fixing Python Dependencies for CambioML Backend"
echo "================================================="

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "📁 Project root: $PROJECT_ROOT"
cd "$PROJECT_ROOT"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip and setuptools
echo "⬆️  Upgrading pip and setuptools..."
pip install --upgrade pip setuptools wheel

# Uninstall potentially conflicting packages
echo "🧹 Cleaning up potentially conflicting packages..."
pip uninstall -y anthropic aiohttp websockets || true

# Install requirements with specific versions
echo "📥 Installing requirements with fixed versions..."
pip install -r requirements.txt

# Verify installation
echo "✅ Verifying installation..."
python -c "
import anthropic
import fastapi
import uvicorn
import websockets
import aiohttp
print('✅ All core packages imported successfully')
print(f'Anthropic version: {anthropic.__version__}')
print(f'FastAPI version: {fastapi.__version__}')
"

echo ""
echo "🎉 Dependencies fixed successfully!"
echo ""
echo "🧪 Test the API key:"
echo "   python scripts/test_api_key.py"
