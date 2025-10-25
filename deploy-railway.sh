#!/bin/bash
# Railway Deployment Script for LightRAG with Vietnamese Embedding

set -e  # Exit on error

echo "🚀 Deploying LightRAG to Railway with Vietnamese Embedding support"
echo "=================================================================="
echo ""

# Check if we're in the right directory
if [ ! -f "Dockerfile.railway" ]; then
    echo "❌ Error: Dockerfile.railway not found!"
    echo "Please run this script from the LightRAG project root directory."
    exit 1
fi

# Check if railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "⚠️  Railway CLI not found. Installing..."
    echo "Run: npm i -g @railway/cli"
    echo "Or visit: https://docs.railway.app/develop/cli"
    exit 1
fi

echo "✅ Railway CLI found"
echo ""

# Show current configuration
echo "📋 Current Configuration:"
echo "  - Builder: DOCKERFILE"
echo "  - Dockerfile: Dockerfile.railway"
echo "  - Python: 3.10"
echo "  - Dependencies: torch>=2.0.0, transformers>=4.30.0"
echo ""

# Check git status
if [[ -n $(git status -s) ]]; then
    echo "⚠️  You have uncommitted changes:"
    git status -s
    echo ""
    read -p "Do you want to commit them? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add Dockerfile.railway railway.json RAILWAY_DEPLOYMENT_FIX_TORCH.md
        git commit -m "fix: Railway deployment with Dockerfile for torch installation"
        echo "✅ Changes committed"
    fi
else
    echo "✅ Working directory is clean"
fi

echo ""
echo "🔄 Pushing to Railway..."
git push origin $(git branch --show-current)

echo ""
echo "🏗️  Building on Railway..."
echo "This may take 5-10 minutes for the first build (torch is ~2GB)"
echo ""

# Deploy using Railway CLI (if available)
if command -v railway &> /dev/null; then
    railway up
else
    echo "💡 Manual deployment:"
    echo "  1. Go to: https://railway.app/dashboard"
    echo "  2. Select your project"
    echo "  3. Railway will automatically detect the push and start building"
    echo "  4. Monitor the build logs for:"
    echo "     ✅ '✅ Torch ... installed successfully'"
    echo "     ✅ '✅ Transformers installed successfully'"
    echo "     ✅ '✅ Vietnamese embedding module loaded'"
    echo "     ✅ '✅ ALL IMPORTS SUCCESSFUL'"
fi

echo ""
echo "📊 Monitoring Tips:"
echo "  - Watch build logs for verification steps"
echo "  - First build will be slow (downloading torch ~2GB)"
echo "  - Subsequent builds will be faster (Docker layer caching)"
echo "  - If build fails, check the logs for specific errors"
echo ""

echo "🔍 Verification Checklist:"
echo "  [ ] Build completed without errors"
echo "  [ ] Server started successfully"
echo "  [ ] Health check passes (GET /health)"
echo "  [ ] Vietnamese embedding available"
echo "  [ ] Can query with Vietnamese text"
echo ""

echo "✅ Deployment initiated!"
echo "Monitor at: https://railway.app/dashboard"
