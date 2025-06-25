#!/bin/bash

echo "🔒 Security Check for CambioML Backend"
echo "====================================="

ISSUES_FOUND=0

# Check if .env exists but is not in .gitignore
if [ -f .env ]; then
    echo "✅ .env file found"
    
    if [ -f .gitignore ]; then
        if grep -q "^\.env$\|^\*\.env$" .gitignore; then
            echo "✅ .env is properly ignored by git"
        else
            echo "❌ .env file exists but is NOT in .gitignore!"
            echo "   This is a SECURITY RISK - your API keys could be committed!"
            ISSUES_FOUND=$((ISSUES_FOUND + 1))
        fi
    else
        echo "❌ No .gitignore file found!"
        echo "   Create .gitignore to prevent committing sensitive files"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi
    
    # Check if .env has actual API key
    if grep -q "your_anthropic_api_key_here" .env; then
        echo "⚠️  .env still contains placeholder API key"
        echo "   Please add your real API key from https://console.anthropic.com/"
    elif grep -q "sk-ant-api03-" .env; then
        echo "✅ .env contains API key"
    else
        echo "⚠️  No API key found in .env"
    fi
else
    echo "⚠️  No .env file found"
    echo "   Run: ./scripts/setup_env.sh to create one"
fi

# Check if any tracked files contain API keys
if [ -d .git ]; then
    echo ""
    echo "🔍 Checking git history for leaked API keys..."
    
    if git log --all --full-history -- .env >/dev/null 2>&1; then
        echo "❌ .env file has been committed to git history!"
        echo "   This is a MAJOR security issue!"
        echo "   You should:"
        echo "   1. Rotate your API key immediately"
        echo "   2. Remove .env from git history"
        echo "   3. Force push to remote repository"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    else
        echo "✅ No .env file in git history"
    fi
    
    # Check for API keys in any committed files
    if git grep -r "sk-ant-api03-" HEAD >/dev/null 2>&1; then
        echo "❌ API keys found in committed files!"
        echo "   Files containing API keys:"
        git grep -l "sk-ant-api03-" HEAD
        echo "   You MUST rotate these keys immediately!"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    else
        echo "✅ No API keys found in committed files"
    fi
fi

# Check file permissions
if [ -f .env ]; then
    PERMS=$(stat -c "%a" .env 2>/dev/null || stat -f "%A" .env 2>/dev/null)
    if [ "$PERMS" = "600" ] || [ "$PERMS" = "0600" ]; then
        echo "✅ .env has secure file permissions (600)"
    else
        echo "⚠️  .env file permissions are $PERMS"
        echo "   Consider: chmod 600 .env"
    fi
fi

echo ""
if [ $ISSUES_FOUND -eq 0 ]; then
    echo "🎉 Security check passed! No issues found."
else
    echo "⚠️  Found $ISSUES_FOUND security issue(s) that need attention!"
    echo ""
    echo "🚨 IMMEDIATE ACTIONS REQUIRED:"
    echo "   1. Rotate any exposed API keys at https://console.anthropic.com/"
    echo "   2. Fix .gitignore to include .env"
    echo "   3. Remove sensitive files from git history if needed"
fi

echo ""
echo "🛡️  Security Best Practices:"
echo "   • Never commit .env files"
echo "   • Use different API keys for dev/staging/prod"
echo "   • Rotate API keys regularly"
echo "   • Use environment variables in production"
echo "   • Monitor API key usage"
