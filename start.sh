#!/bin/bash
# =============================================================================
# 🚨 WEAPONS TRADE DETECTION SYSTEM - Quick Start Script
# =============================================================================

set -e

echo "🚀 Starting Weapons Trade Detection System..."
echo ""

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    if [ -f "backend/.env.example" ]; then
        echo "⚠️  No .env file found. Creating from template..."
        cp backend/.env.example backend/.env
        echo "📝 Please edit backend/.env with your Reddit API credentials"
        echo "   Then run this script again."
        exit 1
    else
        echo "❌ No .env.example found. Please create backend/.env manually."
        exit 1
    fi
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

echo "🐳 Starting Docker containers..."
docker compose up -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 5

echo ""
echo "📦 Checking if LLM models need to be downloaded..."
echo "   (This may take 5-10 minutes on first run)"
docker compose logs -f ollama-setup 2>/dev/null || true

echo ""
echo "✅ All services started!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📍 Access Points:"
echo "   🌐 Frontend:  http://localhost:3000"
echo "   🔧 Backend:   http://localhost:9000"
echo "   📚 API Docs:  http://localhost:9000/docs"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 View logs:    docker compose logs -f backend"
echo "🛑 Stop:         docker compose down"
echo ""

# Open browser (macOS)
if command -v open &> /dev/null; then
    echo "🌐 Opening browser..."
    sleep 2
    open http://localhost:3000
fi

