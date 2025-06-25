#!/bin/bash

echo "🔐 Setting up Environment Variables Securely"
echo "============================================"

# Check if .env already exists
if [ -f .env ]; then
    echo "⚠️  .env file already exists"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Setup cancelled"
        exit 1
    fi
fi

# Copy template
echo "📝 Creating .env from template..."
cp .env.example .env

echo "✅ .env file created"
echo ""
echo "🔑 Please edit .env file and add your ANTHROPIC_API_KEY"
echo "   You can get an API key from: https://console.anthropic.com/"
echo ""
echo "⚠️  SECURITY REMINDERS:"
echo "   • Never commit .env files to git"
echo "   • Never share API keys publicly"
echo "   • Rotate keys regularly"
echo "   • Use different keys for dev/prod"
echo ""

# Check if git is initialized
if [ -d .git ]; then
    # Check if .gitignore exists and has .env
    if [ -f .gitignore ]; then
        if ! grep -q "^\.env$" .gitignore; then
            echo "🛡️  Adding .env to .gitignore for security..."
            echo "" >> .gitignore
            echo "# Environment files - NEVER COMMIT!" >> .gitignore
            echo ".env" >> .gitignore
            echo "*.env" >> .gitignore
        else
            echo "✅ .env already in .gitignore"
        fi
    else
        echo "🛡️  Creating .gitignore with security settings..."
        cat > .gitignore << 'EOF'
# Environment Variables - NEVER COMMIT THESE!
.env
.env.local
.env.production
.env.staging
*.env

# Python
__pycache__/
*.py[cod]
venv/
*.log

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
EOF
    fi
    
    echo "✅ Git security configured"
else
    echo "ℹ️  Not a git repository - skipping git configuration"
fi

echo ""
echo "📋 Next steps:"
echo "   1. Edit .env and add your ANTHROPIC_API_KEY"
echo "   2. Run: source venv/bin/activate"
echo "   3. Run: python scripts/test_api_key.py"
echo "   4. Run: ./scripts/quick_start.sh"
