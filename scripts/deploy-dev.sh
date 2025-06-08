#!/bin/bash
set -e

echo "🚀 Starting Development Deployment..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please copy .env.example to .env and configure it."
    exit 1
fi

# Build and start development environment
docker-compose up --build -d

echo "✅ Development environment started!"
echo "🌐 Application available at: http://localhost:8501"
echo "📋 View logs with: docker-compose logs -f"