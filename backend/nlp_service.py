import sqlite3
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json

class NLPService:
    def __init__(self, db_path: str = 'sif400.db'):
        self.db_path = db_path
        self.stations = ['SIF-401', 'SIF-402', 'SIF-405', 'SIF-407']
        self.thresholds = None  # Will be set by the main app
        
    def get_db_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def set_thresholds(self, thresholds: Dict):
        """Update the thresholds reference from the main application"""
        self.thresholds = thresholds
    
    def process_query(self, query: str) -> str:
        """Process natural language query and return appropriate response"""
        query_lower = query.lower().strip()
        
        # Get current data for context
        current_data = self._get_current_status()
        alerts = self._get_active_alerts()
        
        # Intent classification
        intent = self._classify_intent(query_lower)
        
        # Generate response based on intent
        if intent == 'status_overview':
            return self._generate_status_overview(current_data, alerts)
        elif intent == 'voltage_query':
            return self._generate_voltage_response(query_lower, current_data)
        elif intent == 'current_query':
            return self._generate_current_response(query_lower, current_data)
        elif intent == 'power_query':
            return self._generate_power_response(query_lower, current_data)
        elif intent == 'alert_query':
            return self._generate_alert_response(alerts)
        elif intent == 'trend_query':
            return self._generate_trend_response(query_lower, current_data)
        elif intent == 'station_specific':
            station = self._extract_station(query_lower)
            return self._generate_station_response(station, current_data)
        elif intent == 'historical':
            return self._generate_historical_response(query_lower)
        elif intent == 'comparison':
            return self._generate_comparison_response(current_data)
        else:
            return self._generate_help_response(current_data)
    
    def _classify_intent(self, query: str) -> str:
        """Classify the intent of the user query"""
        
        # Status overview patterns
        status_patterns = [
            r'(how|what).*(status|doing|operating)',
            r'(overall|general|current).*(status|condition)',
            r'(summary|overview)',
            r'how.*(station|everything)',
        ]
        
        # Voltage patterns
        voltage_patterns = [
            r'voltage',
            r'volt',
            r'v\b',
            r'electrical.*potential',
        ]
        
        # Current patterns
        current_patterns = [
            r'current(?!.*status)',  # current but not "current status"
            r'amperage',
            r'amp',
            r'electrical.*current',
        ]
        
        # Power patterns
        power_patterns = [
            r'power',
            r'watt',
            r'consumption',
            r'energy',
        ]
        
        # Alert patterns
        alert_patterns = [
            r'alert',
            r'warning',
            r'problem',
            r'issue',
            r'error',
            r'fault',
            r'anomaly',
        ]
        
        # Trend patterns
        trend_patterns = [
            r'trend',
            r'history',
            r'over.*time',
            r'past.*hour',
            r'changing',
            r'increasing',
            r'decreasing',
        ]
        
        # Station specific patterns
        station_patterns = [
            r'sif[-\s]?40[1257]',
            r'station.*40[1257]',
        ]
        
        # Historical patterns
        historical_patterns = [
            r'yesterday',
            r'last.*week',
            r'past.*day',
            r'historical',
            r'previous',
        ]
        
        # Comparison patterns
        comparison_patterns = [
            r'compar',
            r'differ',
            r'which.*higher',
            r'which.*lower',
            r'best.*perform',
            r'worst.*perform',
        ]
        
        # Check patterns in order of specificity
        if any(re.search(pattern, query) for pattern in alert_patterns):
            return 'alert_query'
        elif any(re.search(pattern, query) for pattern in voltage_patterns):
            return 'voltage_query'
        elif any(re.search(pattern, query) for pattern in current_patterns):
            return 'current_query'
        elif any(re.search(pattern, query) for pattern in power_patterns):
            return 'power_query'
        elif any(re.search(pattern, query) for pattern in station_patterns):
            return 'station_specific'
        elif any(re.search(pattern, query) for pattern in trend_patterns):
            return 'trend_query'
        elif any(re.search(pattern, query) for pattern in historical_patterns):
            return 'historical'
        elif any(re.search(pattern, query) for pattern in comparison_patterns):
            return 'comparison'
        elif any(re.search(pattern, query) for pattern in status_patterns):
            return 'status_overview'
        else:
            return 'general'
    
    def _extract_station(self, query: str) -> str:
        """Extract station ID from query"""
        for station in self.stations:
            if station.lower().replace('-', '') in query.replace('-', '').replace(' ', ''):
                return station
        return None
    
    def _get_current_status(self) -> Dict[str, Any]:
        """Get current status of all stations"""
        with self.get_db_connection() as conn:
            status = {}
            for station_id in self.stations:
                measurement = conn.execute('''
                    SELECT voltage, current, power, status, timestamp FROM measurements 
                    WHERE station_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                ''', (station_id,)).fetchone()
                
                if measurement:
                    status[station_id] = dict(measurement)
            return status
    
    def _get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active alerts"""
        with self.get_db_connection() as conn:
            alerts = conn.execute('''
                SELECT station_id, alert_type, message, severity, timestamp 
                FROM alerts 
                WHERE resolved = FALSE 
                ORDER BY timestamp DESC 
                LIMIT 10
            ''').fetchall()
            return [dict(alert) for alert in alerts]
    
    def _generate_status_overview(self, current_data: Dict, alerts: List) -> str:
        """Generate overall status overview"""
        total_stations = len(self.stations)
        normal_stations = sum(1 for data in current_data.values() if data['status'] == 'normal')
        warning_stations = total_stations - normal_stations
        
        response = f"📊 SIF-400 System Status Overview:\n\n"
        response += f"🟢 Stations Operating Normally: {normal_stations}/{total_stations}\n"
        
        if warning_stations > 0:
            response += f"⚠️ Stations with Warnings: {warning_stations}\n"
        
        response += f"\n📈 Current Readings:\n"
        for station_id, data in current_data.items():
            status_emoji = "🟢" if data['status'] == 'normal' else "⚠️"
            response += f"{status_emoji} {station_id}: {data['voltage']:.1f}V, {data['current']:.1f}A, {data['power']:.1f}W\n"
        
        if alerts:
            response += f"\n🚨 Active Alerts ({len(alerts)}):\n"
            for alert in alerts[:3]:  # Show top 3 alerts
                response += f"• {alert['station_id']}: {alert['message']}\n"
        else:
            response += "\n✅ No active alerts"
        
        return response
    
    def _generate_voltage_response(self, query: str, current_data: Dict) -> str:
        """Generate voltage-specific response"""
        station = self._extract_station(query)
        
        if station and station in current_data:
            data = current_data[station]
            return f"⚡ {station} Voltage: {data['voltage']:.1f}V (Status: {data['status']})"
        else:
            response = "⚡ Current Voltage Readings:\n"
            for station_id, data in current_data.items():
                status_emoji = "🟢" if data['status'] == 'normal' else "⚠️"
                response += f"{status_emoji} {station_id}: {data['voltage']:.1f}V\n"
            
            # Add voltage analysis
            voltages = [data['voltage'] for data in current_data.values()]
            avg_voltage = sum(voltages) / len(voltages)
            response += f"\n📊 Average Voltage: {avg_voltage:.1f}V"
            
            return response
    
    def _generate_current_response(self, query: str, current_data: Dict) -> str:
        """Generate current-specific response"""
        station = self._extract_station(query)
        
        if station and station in current_data:
            data = current_data[station]
            return f"🔌 {station} Current: {data['current']:.1f}A (Status: {data['status']})"
        else:
            response = "🔌 Current Readings:\n"
            for station_id, data in current_data.items():
                status_emoji = "🟢" if data['status'] == 'normal' else "⚠️"
                response += f"{status_emoji} {station_id}: {data['current']:.1f}A\n"
            
            # Add current analysis
            currents = [data['current'] for data in current_data.values()]
            avg_current = sum(currents) / len(currents)
            response += f"\n📊 Average Current: {avg_current:.1f}A"
            
            return response
    
    def _generate_power_response(self, query: str, current_data: Dict) -> str:
        """Generate power-specific response"""
        station = self._extract_station(query)
        
        if station and station in current_data:
            data = current_data[station]
            return f"⚡ {station} Power: {data['power']:.1f}W (Status: {data['status']})"
        else:
            response = "⚡ Current Power Readings:\n"
            total_power = 0
            for station_id, data in current_data.items():
                status_emoji = "🟢" if data['status'] == 'normal' else "⚠️"
                response += f"{status_emoji} {station_id}: {data['power']:.1f}W\n"
                total_power += data['power']
            
            response += f"\n📊 Total System Power: {total_power:.1f}W"
            
            return response
    
    def _generate_alert_response(self, alerts: List) -> str:
        """Generate alert-specific response"""
        if not alerts:
            return "✅ No active alerts. All stations are operating normally."
        
        response = f"🚨 Active Alerts ({len(alerts)}):\n\n"
        for alert in alerts:
            severity_emoji = "🔴" if alert['severity'] == 'critical' else "⚠️"
            response += f"{severity_emoji} {alert['station_id']}: {alert['message']}\n"
        
        return response
    
    def _generate_trend_response(self, query: str, current_data: Dict) -> str:
        """Generate trend analysis response"""
        station = self._extract_station(query)
        
        with self.get_db_connection() as conn:
            if station:
                # Get recent trend for specific station
                trend_data = conn.execute('''
                    SELECT voltage, current, timestamp FROM measurements 
                    WHERE station_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT 10
                ''', (station,)).fetchall()
                
                if len(trend_data) >= 2:
                    recent_voltage = trend_data[0]['voltage']
                    prev_voltage = trend_data[-1]['voltage']
                    voltage_change = recent_voltage - prev_voltage
                    
                    direction = "📈 increasing" if voltage_change > 0 else "📉 decreasing" if voltage_change < 0 else "➡️ stable"
                    
                    return f"📊 {station} Trend Analysis:\nVoltage: {recent_voltage:.1f}V ({direction})\nChange: {voltage_change:+.1f}V over recent readings"
                else:
                    return f"📊 {station}: Current voltage {current_data[station]['voltage']:.1f}V (insufficient data for trend analysis)"
            else:
                # Overall system trend
                response = "📊 System Trend Analysis:\n"
                for station_id in self.stations:
                    if station_id in current_data:
                        response += f"{station_id}: {current_data[station_id]['voltage']:.1f}V, {current_data[station_id]['current']:.1f}A\n"
                
                return response
    
    def _generate_station_response(self, station: str, current_data: Dict) -> str:
        """Generate station-specific response"""
        if station and station in current_data:
            data = current_data[station]
            status_emoji = "🟢" if data['status'] == 'normal' else "⚠️"
            
            response = f"{status_emoji} {station} Detailed Status:\n"
            response += f"⚡ Voltage: {data['voltage']:.1f}V\n"
            response += f"🔌 Current: {data['current']:.1f}A\n"
            response += f"💡 Power: {data['power']:.1f}W\n"
            response += f"📍 Status: {data['status'].title()}\n"
            
            return response
        else:
            return f"❌ Station not found. Available stations: {', '.join(self.stations)}"
    
    def _generate_historical_response(self, query: str) -> str:
        """Generate historical data response"""
        return "📈 Historical data analysis is available. I can show you trends and patterns from the past measurements. What specific time period are you interested in?"
    
    def _generate_comparison_response(self, current_data: Dict) -> str:
        """Generate comparison response"""
        voltages = {station: data['voltage'] for station, data in current_data.items()}
        currents = {station: data['current'] for station, data in current_data.items()}
        powers = {station: data['power'] for station, data in current_data.items()}
        
        highest_voltage = max(voltages, key=voltages.get)
        lowest_voltage = min(voltages, key=voltages.get)
        highest_current = max(currents, key=currents.get)
        lowest_current = min(currents, key=currents.get)
        highest_power = max(powers, key=powers.get)
        
        response = "📊 Station Comparison:\n\n"
        response += f"🔋 Highest Voltage: {highest_voltage} ({voltages[highest_voltage]:.1f}V)\n"
        response += f"🔋 Lowest Voltage: {lowest_voltage} ({voltages[lowest_voltage]:.1f}V)\n"
        response += f"⚡ Highest Current: {highest_current} ({currents[highest_current]:.1f}A)\n"
        response += f"⚡ Lowest Current: {lowest_current} ({currents[lowest_current]:.1f}A)\n"
        response += f"💡 Highest Power: {highest_power} ({powers[highest_power]:.1f}W)\n"
        
        return response
    
    def _generate_help_response(self, current_data: Dict) -> str:
        """Generate help/default response"""
        response = "🤖 I'm your SIF-400 Digital Twin Assistant! I can help you with:\n\n"
        response += "• Station status and readings\n"
        response += "• Voltage, current, and power information\n"
        response += "• Alert monitoring\n"
        response += "• Trend analysis\n"
        response += "• Station comparisons\n\n"
        response += "Try asking: 'What's the status?', 'Show me voltage levels', or 'Any alerts?'\n\n"
        response += "Current system status:\n"
        
        for station_id, data in current_data.items():
            status_emoji = "🟢" if data['status'] == 'normal' else "⚠️"
            response += f"{status_emoji} {station_id}: {data['voltage']:.1f}V, {data['current']:.1f}A\n"
        
        return response