/**
 * WebSocket service for real-time communication with backend
 */
import { io } from 'socket.io-client';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

class WebSocketService {
  constructor() {
    this.socket = null;
    this.clientId = this.generateClientId();
    this.messageHandlers = [];
    this.connectionHandlers = [];
  }

  generateClientId() {
    return `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  connect() {
    if (this.socket?.connected) {
      console.log('Already connected');
      return;
    }

    // Create WebSocket connection
    this.socket = io(BACKEND_URL, {
      path: `/ws/${this.clientId}`,
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5
    });

    // Connection event handlers
    this.socket.on('connect', () => {
      console.log('Connected to backend');
      this.connectionHandlers.forEach(handler => handler(true));
    });

    this.socket.on('disconnect', () => {
      console.log('Disconnected from backend');
      this.connectionHandlers.forEach(handler => handler(false));
    });

    this.socket.on('connect_error', (error) => {
      console.error('Connection error:', error);
    });

    // Message handler
    this.socket.on('message', (data) => {
      this.messageHandlers.forEach(handler => handler(data));
    });
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  sendMessage(message) {
    if (this.socket?.connected) {
      this.socket.emit('message', { message });
    } else {
      console.error('Socket not connected');
    }
  }

  onMessage(handler) {
    this.messageHandlers.push(handler);
    return () => {
      this.messageHandlers = this.messageHandlers.filter(h => h !== handler);
    };
  }

  onConnectionChange(handler) {
    this.connectionHandlers.push(handler);
    return () => {
      this.connectionHandlers = this.connectionHandlers.filter(h => h !== handler);
    };
  }
}

// Singleton instance
const wsService = new WebSocketService();

export default wsService;
