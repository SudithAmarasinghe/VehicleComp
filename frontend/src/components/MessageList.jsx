import React, { useEffect, useRef } from 'react';
import VehicleCard from './VehicleCard';
import { Bot, User } from 'lucide-react';
import './MessageList.css';

const MessageList = ({ messages }) => {
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    return (
        <div className="message-list">
            {messages.map((message, index) => (
                <div
                    key={index}
                    className={`message ${message.role}`}
                    style={{ animationDelay: `${index * 0.1}s` }}
                >
                    <div className="message-avatar">
                        {message.role === 'user' ? (
                            <User size={20} />
                        ) : (
                            <Bot size={20} />
                        )}
                    </div>

                    <div className="message-content">
                        <div className="message-text">
                            {message.content}
                        </div>

                        {message.vehicles && message.vehicles.length > 0 && (
                            <div className="vehicle-grid">
                                {message.vehicles.map((vehicle, idx) => (
                                    <VehicleCard key={idx} vehicle={vehicle} />
                                ))}
                            </div>
                        )}

                        {message.comparison && message.comparison.summary && (
                            <div className="comparison-summary">
                                <h4>Price Comparison</h4>
                                {Object.entries(message.comparison.summary).map(([model, data]) => (
                                    <div key={model} className="comparison-item">
                                        <div className="comparison-model">{model}</div>
                                        <div className="comparison-stats">
                                            <span>Avg: Rs {data.avg_price?.toLocaleString()}</span>
                                            <span>Range: Rs {data.min_price?.toLocaleString()} - Rs {data.max_price?.toLocaleString()}</span>
                                            <span>{data.count} listings</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            ))}

            <div ref={messagesEndRef} />
        </div>
    );
};

export default MessageList;
