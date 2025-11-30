#!/bin/bash

# Trading Prediction App - Quick Start Script

echo "🚀 Starting Trading Prediction App..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker compose is available
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Build and start services
echo "🔨 Building and starting services..."
docker compose up -d --build

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to start..."
sleep 5

# Check service status
echo ""
echo "📊 Service Status:"
docker compose ps

# Health check
echo ""
echo "🏥 Health Check:"

if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs | grep -q "200"; then
    echo "✅ Python API is running (http://localhost:8000)"
else
    echo "❌ Python API is not responding"
fi

if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "200"; then
    echo "✅ Backend is running (http://localhost:3000)"
else
    echo "⚠️  Backend might not be responding (this is normal if no routes are defined at root)"
fi

if curl -s -o /dev/null -w "%{http_code}" http://localhost:80 | grep -q "200"; then
    echo "✅ Frontend is running (http://localhost:80)"
else
    echo "❌ Frontend is not responding"
fi

echo ""
echo "🎉 Application is ready!"
echo ""
echo "📱 Access the application:"
echo "   Frontend:  http://localhost"
echo "   Backend:   http://localhost:3000"
echo "   Python API: http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "📝 Useful commands:"
echo "   View logs:     docker compose logs -f"
echo "   Stop app:      docker compose down"
echo "   Restart:       docker compose restart"
echo ""

