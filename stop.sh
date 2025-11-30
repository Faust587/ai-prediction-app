#!/bin/bash

# Trading Prediction App - Stop Script

echo "🛑 Stopping Trading Prediction App..."
echo ""

# Stop services
docker compose down

echo ""
echo "✅ All services stopped"
echo ""
echo "💡 To remove all data and volumes, run:"
echo "   docker compose down -v"
echo ""

