import React, { useState } from 'react';
import { Send, Loader2 } from 'lucide-react';
import './ChatInput.css';

const ChatInput = ({ onSendMessage, isLoading }) => {
    const [message, setMessage] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (message.trim() && !isLoading) {
            onSendMessage(message);
            setMessage('');
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    };

    return (
        <form className="chat-input" onSubmit={handleSubmit}>
            <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about vehicle prices... (e.g., 'Toyota Aqua 2018 price')"
                disabled={isLoading}
                className="message-input"
            />

            <button
                type="submit"
                className="send-button"
                disabled={!message.trim() || isLoading}
            >
                {isLoading ? (
                    <Loader2 size={20} className="spinner" />
                ) : (
                    <Send size={20} />
                )}
            </button>
        </form>
    );
};

export default ChatInput;
