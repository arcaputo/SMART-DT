# SIF-400 Digital Twin - Native Implementation

This is a native implementation of the SIF-400 Digital Twin system that provides real-time monitoring and analytics for power stations 401, 402, 405, and 407. The system includes voltage, current, and power monitoring with natural language query capabilities.

## Architecture

The system consists of two main components:

1. **Python Backend** (`/backend/`)
   - Flask REST API server
   - SQLite database for data storage
   - Real-time data simulation
   - Natural language processing service
   - Alert monitoring and management

2. **React Frontend** (`/frontend/`)
   - Modern React application with Tailwind CSS
   - Real-time dashboard with station cards
   - Interactive chat interface
   - Alert management system

## Features

- **Real-time Monitoring**: Live voltage, current, and power readings
- **Natural Language Interface**: Ask questions about station status in plain English
- **Alert System**: Automatic anomaly detection and alerting
- **Trend Analysis**: Historical data visualization
- **Station Comparison**: Compare performance across stations
- **Responsive Design**: Works on desktop and mobile devices

## Installation & Setup

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Start the backend server:
```bash
python app.py
```

The backend will start on `http://localhost:5001`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The frontend will start on `http://localhost:3001`

## Usage

1. **Start the Backend**: Run the Python Flask server first
2. **Start the Frontend**: Run the React development server
3. **Access the Application**: Open your browser to `http://localhost:3001`

### Natural Language Queries

The system supports various types of natural language queries:

- **Status Overview**: "What's the current status?", "How are the stations doing?"
- **Voltage Queries**: "Show me voltage levels", "What's the voltage of SIF-401?"
- **Current Queries**: "What's the current reading?", "Show me amperage"
- **Power Queries**: "What's the power consumption?", "Show me power readings"
- **Alert Queries**: "Any alerts?", "Show me problems"
- **Trend Analysis**: "Show me trends", "How is voltage changing?"
- **Station Specific**: "Tell me about SIF-401", "Status of station 402"
- **Comparisons**: "Which station has higher voltage?", "Compare the stations"

## Database Schema

The SQLite database contains three main tables:

- **stations**: Station metadata (ID, name)
- **measurements**: Real-time measurements (voltage, current, power, status)
- **alerts**: System alerts and warnings

## API Endpoints

- `GET /api/stations` - Get all stations
- `GET /api/stations/{id}/latest` - Get latest measurement for a station
- `GET /api/stations/{id}/history` - Get historical data for a station
- `GET /api/current-status` - Get current status of all stations
- `GET /api/alerts` - Get active alerts
- `POST /api/chat` - Process natural language queries

## Monitoring Ranges

- **Voltage**: Normal range 216-224V (warnings outside this range)
- **Current**: Normal range 14.5-15.8A (warnings outside this range)
- **Power**: Calculated as Voltage × Current

## Development

### Adding New Features

1. **Backend**: Add new endpoints in `app.py`, extend NLP service in `nlp_service.py`
2. **Frontend**: Modify React components in the `src/` directory

### Database Management

The database is automatically initialized when the backend starts. Data is persisted in `sif400.db`.

### Customization

- **Station Configuration**: Modify station IDs in both backend and frontend
- **Monitoring Ranges**: Update thresholds in `app.py` and `nlp_service.py`
- **UI Styling**: Customize appearance in React components using Tailwind CSS

## Troubleshooting

### Common Issues

1. **Connection Errors**: Ensure backend is running on port 5001
2. **Database Issues**: Delete `sif400.db` to reset the database
3. **Port Conflicts**: Change ports in the configuration files if needed

### Backend Logs

Check the console output of the Python server for error messages and debugging information.

### Frontend Debugging

Use browser developer tools to check for network errors and console messages.

## Future Enhancements

- Integration with real SIF-400 hardware
- Advanced analytics and machine learning
- Mobile application
- Multi-user support and authentication
- Advanced alerting and notifications
- Historical data export capabilities