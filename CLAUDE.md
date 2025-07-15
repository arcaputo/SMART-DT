# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a SIF-400 Digital Twin system - a full-stack web application for real-time monitoring of power stations (SIF-401, 402, 405, 407). The system tracks voltage, current, and power measurements with natural language query capabilities and alert management.

## Development Commands

### Quick Start
- **Start entire system**: `./start.sh` (automated startup with health checks)
- **Stop system**: `./stop.sh` (graceful shutdown)

### Backend (Python Flask)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py  # Starts on http://localhost:5001
```

### Frontend (React)
```bash
cd frontend
npm install
npm start      # Starts on http://localhost:3000
npm run build  # Production build
npm test       # Run tests
```

### Database Management
- **Database file**: `backend/sif400.db` (SQLite, auto-created)
- **Reset database**: Delete `sif400.db` file and restart backend
- **Tables**: stations, measurements, alerts

## Architecture

### Backend (`/backend/`)
- **`app.py`**: Flask REST API server with real-time data simulation
  - Multi-threaded measurement generation for 4 stations
  - SQLite database management with auto-initialization
  - CORS-enabled endpoints for frontend integration
  - Alert system with configurable thresholds
- **`nlp_service.py`**: Natural language processing for chat interface
  - Intent classification and contextual responses
  - Station-specific query handling

### Frontend (`/frontend/`)
- **`src/SIF400DigitalTwin.jsx`**: Main dashboard component with live station cards
- **`src/App.js`**: Root React component
- **React + Tailwind CSS** with lucide-react icons
- **Proxy configuration** to backend API in package.json

### Key API Endpoints
- `GET /api/stations` - Station metadata
- `GET /api/stations/{id}/latest` - Latest measurements
- `GET /api/current-status` - All stations current status
- `GET /api/alerts` - Active alerts
- `POST /api/chat` - Natural language queries

## Configuration

### Monitoring Thresholds
- **Voltage**: Normal range 216-224V (configured in both backend services)
- **Current**: Normal range 14.5-15.8A
- **Power**: Calculated as Voltage × Current

### Station IDs
- SIF-401, SIF-402, SIF-405, SIF-407 (hardcoded in both frontend and backend)

### Development Ports
- Backend: 5001 (Flask development server)
- Frontend: 3001 (React development server)
- Frontend proxies API calls to backend via package.json proxy setting

## Data Flow

1. **Backend simulation thread** generates realistic measurements every few seconds
2. **SQLite database** stores stations, measurements, and alerts
3. **Frontend polls** backend APIs for live updates
4. **Chat interface** processes natural language queries through NLP service
5. **Alert system** monitors thresholds and generates warnings

## Testing

- Frontend tests: `npm test` (Jest/React Testing Library)
- No backend test suite currently configured
- Manual testing via browser at http://localhost:3000

## Troubleshooting

- **Database issues**: Delete `sif400.db` to reset
- **Port conflicts**: Backend uses port 5001 to avoid macOS AirPlay conflicts on 5000
- **Virtual environment**: Ensure `source venv/bin/activate` before running Python
- **Dependencies**: Run install commands if modules are missing