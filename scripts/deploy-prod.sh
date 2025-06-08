#!/bin/bash
set -e

echo "🚀 Starting Production Deployment..."

# Validate required environment variables
required_vars=("OPENAI_API_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Required environment variable $var is not set"
        exit 1
    fi
done

# Build and start production environment
docker-compose -f docker-compose.prod.yml up --build -d

echo "✅ Production environment started!"
echo "🌐 Application available at: http://localhost:8501"
echo "📋 View logs with: docker-compose -f docker-compose.prod.yml logs -f"
echo "🔍 Check health: curl http://localhost:8501/_stcore/health"