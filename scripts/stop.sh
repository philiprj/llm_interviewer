#!/bin/bash
set -e

echo "🛑 Stopping services..."

# Stop development
docker-compose down

# Stop production
docker-compose -f docker-compose.prod.yml down

echo "✅ All services stopped!"