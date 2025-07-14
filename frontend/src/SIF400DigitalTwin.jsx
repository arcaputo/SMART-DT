import React, { useState, useEffect, useRef } from 'react';
import { Activity, AlertTriangle, CheckCircle, MessageSquare, Send, Zap, TrendingUp, Bot } from 'lucide-react';

const SIF400DigitalTwin = () => {
  // State management
  const [stationData, setStationData] = useState({});
  const [alerts, setAlerts] = useState([]);
  const [chatMessages, setChatMessages] = useState([
    { role: 'assistant', content: 'Hello! I\'m your SIF-400 Digital Twin Assistant. Ask me anything about the station\'s voltage, current, and power status.' }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const chatEndRef = useRef(null);

  // API base URL
  const API_BASE = 'http://localhost:5000/api';

  // Fetch current station status
  const fetchStationStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/current-status`);
      if (response.ok) {
        const data = await response.json();
        setStationData(data);
        setConnectionStatus('connected');
      } else {
        setConnectionStatus('error');
      }
    } catch (error) {
      console.error('Error fetching station status:', error);
      setConnectionStatus('error');
    }
  };

  // Fetch alerts
  const fetchAlerts = async () => {
    try {
      const response = await fetch(`${API_BASE}/alerts`);
      if (response.ok) {
        const data = await response.json();
        setAlerts(data);
      }
    } catch (error) {
      console.error('Error fetching alerts:', error);
    }
  };

  // Real-time data updates
  useEffect(() => {
    // Initial fetch
    fetchStationStatus();
    fetchAlerts();
    
    // Set up polling for real-time updates
    const interval = setInterval(() => {
      fetchStationStatus();
      fetchAlerts();
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  // Auto-scroll chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  // Handle chat submission
  const handleChatSubmit = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage;
    setInputMessage('');
    setChatMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage }),
      });

      if (response.ok) {
        const data = await response.json();
        setChatMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
      } else {
        setChatMessages(prev => [...prev, {
          role: 'assistant',
          content: 'I apologize, but I encountered an error processing your request. Please try again.'
        }]);
      }
    } catch (error) {
      console.error('Error in chat:', error);
      setChatMessages(prev => [...prev, {
        role: 'assistant',
        content: 'I\'m having trouble connecting to the server. Please check your connection and try again.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  // Station Card Component
  const StationCard = ({ stationId, data }) => {
    if (!data) return null;
    
    const isWarning = data.status === 'warning';

    return (
      <div className={`bg-white rounded-xl shadow-lg p-6 transition-all duration-300 ${
        isWarning ? 'ring-2 ring-orange-400' : ''
      }`}>
        <div className="flex justify-between items-start mb-4">
          <h3 className="text-lg font-semibold text-gray-800">{stationId}</h3>
          <div className={`p-2 rounded-full ${
            isWarning ? 'bg-orange-100' : 'bg-green-100'
          }`}>
            {isWarning ? (
              <AlertTriangle className="w-5 h-5 text-orange-600" />
            ) : (
              <CheckCircle className="w-5 h-5 text-green-600" />
            )}
          </div>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-blue-600" />
              <span className="text-sm text-gray-600">Voltage</span>
            </div>
            <span className="text-xl font-bold text-gray-800">
              {data.voltage?.toFixed(1) || 'N/A'} V
            </span>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-purple-600" />
              <span className="text-sm text-gray-600">Current</span>
            </div>
            <span className="text-xl font-bold text-gray-800">
              {data.current?.toFixed(1) || 'N/A'} A
            </span>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-green-600" />
              <span className="text-sm text-gray-600">Power</span>
            </div>
            <span className="text-xl font-bold text-gray-800">
              {data.power?.toFixed(1) || 'N/A'} W
            </span>
          </div>

          <div className="mt-4 h-16">
            <div className="flex items-end h-full gap-1">
              {data.trend && data.trend.slice(-10).map((point, idx) => {
                const height = ((point.voltage - 215) / 10) * 100;
                return (
                  <div
                    key={idx}
                    className="flex-1 bg-blue-400 rounded-t opacity-70 transition-all duration-300"
                    style={{ height: `${Math.max(height, 5)}%` }}
                  />
                );
              })}
            </div>
            <div className="text-xs text-gray-500 mt-1">Voltage Trend</div>
          </div>
        </div>
      </div>
    );
  };

  // Connection status indicator
  const ConnectionIndicator = () => {
    const getStatusColor = () => {
      switch (connectionStatus) {
        case 'connected': return 'bg-green-500';
        case 'error': return 'bg-red-500';
        default: return 'bg-yellow-500';
      }
    };

    const getStatusText = () => {
      switch (connectionStatus) {
        case 'connected': return 'Connected';
        case 'error': return 'Connection Error';
        default: return 'Connecting...';
      }
    };

    return (
      <div className="flex items-center gap-2">
        <div className={`w-3 h-3 rounded-full ${getStatusColor()} ${connectionStatus === 'connected' ? 'animate-pulse' : ''}`}></div>
        <span className="text-sm text-gray-600">{getStatusText()}</span>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-indigo-100 rounded-xl">
                <Activity className="w-8 h-8 text-indigo-600" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-800">SIF-400 Digital Twin</h1>
                <p className="text-gray-600">Real-time Voltage, Current & Power Monitoring</p>
              </div>
            </div>
            <ConnectionIndicator />
          </div>
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Station Cards */}
          <div className="lg:col-span-2">
            {connectionStatus === 'connected' ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(stationData).map(([stationId, data]) => (
                  <StationCard key={stationId} stationId={stationId} data={data} />
                ))}
              </div>
            ) : (
              <div className="bg-white rounded-xl shadow-lg p-6 text-center">
                <div className="text-gray-500">
                  {connectionStatus === 'error' ? (
                    <div>
                      <AlertTriangle className="w-12 h-12 mx-auto mb-4 text-red-500" />
                      <p>Unable to connect to the backend server.</p>
                      <p className="text-sm mt-2">Please ensure the Python backend is running on port 5000.</p>
                    </div>
                  ) : (
                    <div>
                      <Activity className="w-12 h-12 mx-auto mb-4 animate-spin text-blue-500" />
                      <p>Connecting to station data...</p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Alerts Section */}
            {alerts.length > 0 && (
              <div className="mt-6 bg-orange-50 rounded-xl p-4">
                <h3 className="font-semibold text-orange-800 mb-3 flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5" />
                  Active Alerts
                </h3>
                <div className="space-y-2">
                  {alerts.slice(0, 5).map(alert => (
                    <div key={alert.id} className="bg-white rounded-lg p-3 flex justify-between items-center">
                      <div>
                        <span className="font-medium text-gray-800">{alert.station_id}</span>
                        <span className="text-gray-600 ml-2">{alert.message}</span>
                      </div>
                      <span className="text-xs text-gray-500">{new Date(alert.timestamp).toLocaleTimeString()}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Chat Interface */}
          <div className="bg-white rounded-xl shadow-lg p-6 flex flex-col h-[600px]">
            <div className="flex items-center gap-3 mb-4 pb-4 border-b">
              <div className="p-2 bg-indigo-100 rounded-lg">
                <Bot className="w-6 h-6 text-indigo-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-800">AI Assistant</h3>
                <p className="text-sm text-gray-600">Ask about station status</p>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto mb-4 space-y-3">
              {chatMessages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg p-3 whitespace-pre-wrap ${
                      msg.role === 'user'
                        ? 'bg-indigo-600 text-white'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {msg.content}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 rounded-lg p-3">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            <form onSubmit={handleChatSubmit} className="flex gap-2">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Ask about voltage, current, power, or alerts..."
                className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                disabled={isLoading || connectionStatus !== 'connected'}
              />
              <button
                type="submit"
                disabled={isLoading || !inputMessage.trim() || connectionStatus !== 'connected'}
                className="p-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <Send className="w-5 h-5" />
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SIF400DigitalTwin;