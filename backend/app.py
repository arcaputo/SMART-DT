from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import datetime
import random
import threading
import time
import os
from contextlib import contextmanager
from nlp_service import NLPService

app = Flask(__name__)
CORS(app)

# Database setup
DATABASE = 'sif400.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@contextmanager
def get_db():
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS stations (
                id INTEGER PRIMARY KEY,
                station_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                station_id TEXT NOT NULL,
                voltage REAL NOT NULL,
                current REAL NOT NULL,
                power REAL NOT NULL,
                status TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (station_id) REFERENCES stations (station_id)
            );
            
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                station_id TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                message TEXT NOT NULL,
                severity TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (station_id) REFERENCES stations (station_id)
            );
        ''')
        
        # Initialize stations if they don't exist
        stations = ['SIF-401', 'SIF-402', 'SIF-405', 'SIF-407']
        for station in stations:
            conn.execute(
                'INSERT OR IGNORE INTO stations (station_id, name) VALUES (?, ?)',
                (station, f'Station {station}')
            )
        
        conn.commit()

class StationSimulator:
    def __init__(self):
        self.stations = {
            'SIF-401': {'voltage': 220.0, 'current': 15.2, 'status': 'normal'},
            'SIF-402': {'voltage': 218.0, 'current': 14.8, 'status': 'normal'},
            'SIF-405': {'voltage': 221.0, 'current': 15.5, 'status': 'normal'},
            'SIF-407': {'voltage': 219.0, 'current': 15.1, 'status': 'normal'}
        }
        self.running = False
        self.thread = None
        # Dynamic thresholds - can be updated via API
        self.thresholds = {
            'voltage_min': 216.0,
            'voltage_max': 224.0,
            'current_min': 14.5,
            'current_max': 15.8
        }
    
    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._simulate_data)
            self.thread.daemon = True
            self.thread.start()
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
    
    def _simulate_data(self):
        while self.running:
            with get_db() as conn:
                for station_id, data in self.stations.items():
                    # Generate realistic variations
                    voltage_variation = (random.random() - 0.5) * 2
                    current_variation = (random.random() - 0.5) * 0.5
                    
                    data['voltage'] = max(215, min(225, data['voltage'] + voltage_variation))
                    data['current'] = max(14, min(16, data['current'] + current_variation))
                    data['power'] = data['voltage'] * data['current']
                    
                    # Determine status and create alerts using dynamic thresholds
                    status = 'normal'
                    if data['voltage'] < self.thresholds['voltage_min'] or data['voltage'] > self.thresholds['voltage_max']:
                        status = 'warning'
                        self._create_alert(conn, station_id, 'voltage', 
                                         f'Voltage anomaly: {data["voltage"]:.1f}V (threshold: {self.thresholds["voltage_min"]:.1f}-{self.thresholds["voltage_max"]:.1f}V)', 'warning')
                    elif data['current'] < self.thresholds['current_min'] or data['current'] > self.thresholds['current_max']:
                        status = 'warning'
                        self._create_alert(conn, station_id, 'current', 
                                         f'Current anomaly: {data["current"]:.1f}A (threshold: {self.thresholds["current_min"]:.1f}-{self.thresholds["current_max"]:.1f}A)', 'warning')
                    
                    data['status'] = status
                    
                    # Insert measurement
                    conn.execute('''
                        INSERT INTO measurements (station_id, voltage, current, power, status)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (station_id, data['voltage'], data['current'], data['power'], status))
                
                conn.commit()
            
            time.sleep(2)  # Update every 2 seconds
    
    def _create_alert(self, conn, station_id, alert_type, message, severity):
        # Check if similar unresolved alert exists
        existing = conn.execute('''
            SELECT id FROM alerts 
            WHERE station_id = ? AND alert_type = ? AND resolved = FALSE
            AND timestamp > datetime('now', '-5 minutes')
        ''', (station_id, alert_type)).fetchone()
        
        if not existing:
            conn.execute('''
                INSERT INTO alerts (station_id, alert_type, message, severity)
                VALUES (?, ?, ?, ?)
            ''', (station_id, alert_type, message, severity))

# Initialize simulator and NLP service
simulator = StationSimulator()
nlp_service = NLPService()

@app.route('/api/stations', methods=['GET'])
def get_stations():
    with get_db() as conn:
        stations = conn.execute('SELECT * FROM stations').fetchall()
        return jsonify([dict(row) for row in stations])

@app.route('/api/stations/<station_id>/latest', methods=['GET'])
def get_latest_measurement(station_id):
    with get_db() as conn:
        measurement = conn.execute('''
            SELECT * FROM measurements 
            WHERE station_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''', (station_id,)).fetchone()
        
        if measurement:
            return jsonify(dict(measurement))
        else:
            return jsonify({'error': 'Station not found'}), 404

@app.route('/api/stations/<station_id>/history', methods=['GET'])
def get_station_history(station_id):
    limit = request.args.get('limit', 20, type=int)
    with get_db() as conn:
        measurements = conn.execute('''
            SELECT * FROM measurements 
            WHERE station_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (station_id, limit)).fetchall()
        
        return jsonify([dict(row) for row in measurements])

@app.route('/api/current-status', methods=['GET'])
def get_current_status():
    status = {}
    with get_db() as conn:
        for station_id in ['SIF-401', 'SIF-402', 'SIF-405', 'SIF-407']:
            measurement = conn.execute('''
                SELECT voltage, current, power, status, timestamp FROM measurements 
                WHERE station_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 1
            ''', (station_id,)).fetchone()
            
            if measurement:
                # Get recent trend data
                trend = conn.execute('''
                    SELECT voltage, current, timestamp FROM measurements 
                    WHERE station_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT 20
                ''', (station_id,)).fetchall()
                
                status[station_id] = {
                    'voltage': measurement['voltage'],
                    'current': measurement['current'],
                    'power': measurement['power'],
                    'status': measurement['status'],
                    'timestamp': measurement['timestamp'],
                    'trend': [dict(row) for row in trend]
                }
    
    return jsonify(status)

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    with get_db() as conn:
        alerts = conn.execute('''
            SELECT * FROM alerts 
            WHERE resolved = FALSE 
            ORDER BY timestamp DESC 
            LIMIT 10
        ''', ).fetchall()
        
        return jsonify([dict(row) for row in alerts])

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '')
    
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    # Use NLP service to process the query
    response = nlp_service.process_query(message)
    
    return jsonify({'response': response})

@app.route('/api/thresholds', methods=['GET'])
def get_thresholds():
    return jsonify(simulator.thresholds)

@app.route('/api/thresholds', methods=['PUT'])
def update_thresholds():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Threshold data is required'}), 400
    
    # Validate threshold values
    required_fields = ['voltage_min', 'voltage_max', 'current_min', 'current_max']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
        if not isinstance(data[field], (int, float)) or data[field] < 0:
            return jsonify({'error': f'Invalid value for {field}: must be a positive number'}), 400
    
    # Validate logical constraints
    if data['voltage_min'] >= data['voltage_max']:
        return jsonify({'error': 'voltage_min must be less than voltage_max'}), 400
    if data['current_min'] >= data['current_max']:
        return jsonify({'error': 'current_min must be less than current_max'}), 400
    
    # Update thresholds
    simulator.thresholds.update(data)
    
    # Update NLP service with new thresholds
    nlp_service.set_thresholds(simulator.thresholds)
    
    return jsonify({
        'message': 'Thresholds updated successfully',
        'thresholds': simulator.thresholds
    })


if __name__ == '__main__':
    init_db()
    # Initialize NLP service with current thresholds
    nlp_service.set_thresholds(simulator.thresholds)
    simulator.start()
    try:
        app.run(debug=True, host='0.0.0.0', port=5001)
    finally:
        simulator.stop()