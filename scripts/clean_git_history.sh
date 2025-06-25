#!/bin/bash

echo "🧹 Git History Cleanup Tool"
echo "=========================="
echo ""
echo "⚠️  WARNING: This will rewrite git history!"
echo "   Only run this if you've accidentally committed sensitive files"
echo "   Make sure all team members are aware before proceeding"
echo ""

read -p "Are you sure you want to proceed? (type 'yes' to continue): " -r
if [ "$REPLY" != "yes" ]; then
    echo "❌ Operation cancelled"
    exit 1
fi

echo ""
echo "🔍 Checking for sensitive files in git history..."

# Check if .env was ever committed
if git log --all --full-history -- .env >/dev/null 2>&1; then
    echo "❌ Found .env in git history"
    
    echo "🧹 Removing .env from git history..."
    git filter-branch --force --index-filter \
        'git rm --cached --ignore-unmatch .env' \
        --prune-empty --tag-name-filter cat -- --all
    
    echo "✅ .env removed from git history"
fi

# Check for API keys in any files
if git log --all -S "sk-ant-api03-" --oneline | head -1 >/dev/null 2>&1; then
    echo "❌ Found API keys in git history"
    echo "   Manual cleanup required for files containing API keys"
    echo "   Files that may contain API keys:"
    git log --all -S "sk-ant-api03-" --name-only --pretty=format: | sort -u
fi

echo ""
echo "🗑️  Cleaning up git references..."
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo ""
echo "✅ Git history cleanup completed"
echo ""
echo "📤 Next steps:"
echo "   1. Force push to remote: git push origin --force --all"
echo "   2. Force push tags: git push origin --force --tags"
echo "   3. Notify team members to re-clone the repository"
echo "   4. Rotate any API keys that were exposed"
