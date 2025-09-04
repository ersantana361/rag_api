#!/bin/bash
# Test script for Docker Compose setup

echo "🐳 Testing Docker Compose Setup"
echo "================================"

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📋 Creating .env file from .env.dev..."
    cp .env.dev .env
    echo "✅ Environment file created"
    echo "⚠️  Please edit .env and add your OpenAI API key"
fi

# Validate Docker Compose configuration
echo "🔍 Validating Docker Compose configuration..."
if docker compose config > /dev/null 2>&1; then
    echo "✅ Docker Compose configuration is valid"
else
    echo "❌ Docker Compose configuration has errors"
    docker compose config
    exit 1
fi

# Check if ports are available
echo "🔌 Checking if ports 8000 and 8080 are available..."
if lsof -Pi :8000 -sTCP:LISTEN -t > /dev/null 2>&1; then
    echo "⚠️  Port 8000 is already in use"
fi

if lsof -Pi :8080 -sTCP:LISTEN -t > /dev/null 2>&1; then
    echo "⚠️  Port 8080 is already in use"
fi

echo ""
echo "🚀 Ready to start! Run the following commands:"
echo ""
echo "1. Edit .env and add your OpenAI API key:"
echo "   nano .env"
echo ""
echo "2. Start the services:"
echo "   docker compose up --build"
echo ""
echo "3. Access the services:"
echo "   - RAG API: http://localhost:8000"
echo "   - Weaviate: http://localhost:8080"
echo "   - API Documentation: http://localhost:8000/docs"
echo ""
echo "4. Test the API:"
echo "   curl http://localhost:8000/health"
echo ""
echo "✅ Setup validation complete!"