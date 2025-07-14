#!/bin/bash

# SIF-400 Digital Twin Stop Script

echo "🛑 Stopping SIF-400 Digital Twin System..."

# Kill Python backend processes
echo "🔧 Stopping Python backend..."
pkill -f "python app.py" 2>/dev/null
pkill -f "flask" 2>/dev/null

# Kill React frontend processes
echo "🎨 Stopping React frontend..."
pkill -f "react-scripts start" 2>/dev/null
pkill -f "npm start" 2>/dev/null

# Kill any remaining Node.js processes related to our app
pkill -f "node.*react-scripts" 2>/dev/null

# Wait a moment for graceful shutdown
sleep 2

# Force kill if processes are still running
pkill -9 -f "python app.py" 2>/dev/null
pkill -9 -f "react-scripts start" 2>/dev/null

echo "✅ All services stopped"
echo "📊 Backend (port 5000) - stopped"
echo "🖥️  Frontend (port 3000) - stopped"