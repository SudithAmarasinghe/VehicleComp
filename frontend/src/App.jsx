import React, { useState, useEffect } from 'react';
import MessageList from './components/MessageList';
import ChatInput from './components/ChatInput';
import { Car, Wifi, WifiOff } from 'lucide-react';
import './App.css';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

function App() {
    const [messages, setMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [isConnected, setIsConnected] = useState(false);
    const [ws, setWs] = useState(null);
    const [clientId] = useState(`client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);

    useEffect(() => {
        // Connect to WebSocket
        connectWebSocket();

        return () => {
            if (ws) {
                ws.close();
            }
        };
    }, []);

    const connectWebSocket = () => {
        try {
            const websocket = new WebSocket(`ws://localhost:8000/ws/${clientId}`);

            websocket.onopen = () => {
                console.log('WebSocket connected');
                setIsConnected(true);
            };

            websocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                console.log('Received:', data);

                if (data.type === 'system') {
                    // System message
                    setMessages(prev => [...prev, {
                        role: 'assistant',
                        content: data.message
                    }]);
                } else if (data.type === 'typing') {
                    // Typing indicator (optional)
                    setIsLoading(true);
                } else if (data.type === 'response') {
                    // Agent response
                    setIsLoading(false);
                    setMessages(prev => [...prev, {
                        role: 'assistant',
                        content: data.message,
                        vehicles: data.vehicles || [],
                        comparison: data.comparison || {}
                    }]);
                } else if (data.type === 'error') {
                    setIsLoading(false);
                    setMessages(prev => [...prev, {
                        role: 'assistant',
                        content: `Error: ${data.message}`
                    }]);
                }
            };

            websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
                setIsConnected(false);
            };

            websocket.onclose = () => {
                console.log('WebSocket disconnected');
                setIsConnected(false);

                // Attempt to reconnect after 3 seconds
                setTimeout(() => {
                    console.log('Attempting to reconnect...');
                    connectWebSocket();
                }, 3000);
            };

            setWs(websocket);
        } catch (error) {
            console.error('Failed to connect:', error);
            setIsConnected(false);
        }
    };

    const handleSendMessage = (message) => {
        if (!ws || ws.readyState !== WebSocket.OPEN) {
            alert('Not connected to server. Please wait...');
            return;
        }

        // Add user message to UI
        setMessages(prev => [...prev, {
            role: 'user',
            content: message
        }]);

        // Send to backend
        ws.send(JSON.stringify({ message }));
        setIsLoading(true);
    };

    return (
        <div className="app">
            <div className="chat-container">
                <div className="chat-header">
                    <div className="header-content">
                        <div className="header-icon">
                            <Car size={28} />
                        </div>
                        <div className="header-text">
                            <h1>Vehicle Market AI</h1>
                            <p>Sri Lankan Vehicle Price Assistant</p>
                        </div>
                    </div>

                    <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
                        {isConnected ? (
                            <>
                                <Wifi size={16} />
                                <span>Connected</span>
                            </>
                        ) : (
                            <>
                                <WifiOff size={16} />
                                <span>Disconnected</span>
                            </>
                        )}
                    </div>
                </div>

                <MessageList messages={messages} />

                <ChatInput
                    onSendMessage={handleSendMessage}
                    isLoading={isLoading}
                />
            </div>
        </div>
    );
}

export default App;
