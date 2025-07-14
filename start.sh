#!/bin/bash

# SIF-400 Digital Twin Startup Script

echo "🚀 Starting SIF-400 Digital Twin System..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

# Function to start backend
start_backend() {
    echo "🔧 Starting Python backend..."
    cd backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies if needed
    if [ ! -f "requirements_installed.flag" ]; then
        echo "📦 Installing Python dependencies..."
        pip install -r requirements.txt
        touch requirements_installed.flag
    fi
    
    # Start the Flask server
    echo "🌐 Starting Flask server on port 5000..."
    python app.py &
    BACKEND_PID=$!
    cd ..
    
    echo "✅ Backend started (PID: $BACKEND_PID)"
}

# Function to start frontend
start_frontend() {
    echo "🎨 Starting React frontend..."
    cd frontend
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo "📦 Installing Node.js dependencies..."
        npm install
    fi
    
    # Start the React development server
    echo "🌐 Starting React development server on port 3000..."
    npm start &
    FRONTEND_PID=$!
    cd ..
    
    echo "✅ Frontend started (PID: $FRONTEND_PID)"
}

# Function to cleanup on exit
cleanup() {
    echo "🛑 Shutting down services..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    
    # Kill any remaining processes
    pkill -f "python app.py" 2>/dev/null
    pkill -f "react-scripts start" 2>/dev/null
    
    echo "✅ Services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start services
start_backend
sleep 3  # Give backend time to start
start_frontend

echo ""
echo "🎉 SIF-400 Digital Twin is starting up!"
echo "📊 Backend API: http://localhost:5000"
echo "🖥️  Frontend UI: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for services to start
sleep 5

# Check if services are running
if curl -s http://localhost:5000/api/stations > /dev/null 2>&1; then
    echo "✅ Backend is running and responding"
else
    echo "⚠️  Backend may not be fully started yet"
fi

# Keep script running
wait