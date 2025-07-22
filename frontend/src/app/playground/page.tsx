'use client';

import React, { useState, useRef, useEffect } from 'react';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'alith';
  timestamp: Date;
}

interface Service {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'inactive';
}

export default function PlaygroundPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: 'Hello! I\'m Alith, your AI assistant from Metis. How can I help you today?',
      sender: 'alith',
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Placeholder services - you can replace this with actual data later
  const [services] = useState<Service[]>([
    {
      id: '1',
      name: 'Weather API',
      description: 'Get current weather data',
      status: 'active'
    },
    {
      id: '2',
      name: 'Translation Service',
      description: 'Translate text between languages',
      status: 'active'
    },
    {
      id: '3',
      name: 'Image Recognition',
      description: 'Analyze and describe images',
      status: 'inactive'
    }
  ]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Send to Alith API
      const response = await fetch('/api/v1/alith/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: inputMessage,
          context: 'playground',
          timestamp: new Date().toISOString()
        })
      });

      if (response.ok) {
        const data = await response.json();
        const alithMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: data.response || 'I received your message but couldn\'t process it properly.',
          sender: 'alith',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, alithMessage]);
      } else {
        throw new Error('Failed to get response from Alith');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        sender: 'alith',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const executeService = async (serviceId: string) => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/alith/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          serviceId: serviceId,
          parameters: {},
          context: 'playground'
        })
      });

      if (response.ok) {
        const data = await response.json();
        const serviceMessage: Message = {
          id: Date.now().toString(),
          content: `Service executed successfully: ${data.result || 'Service completed'}`,
          sender: 'alith',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, serviceMessage]);
      }
    } catch (error) {
      console.error('Error executing service:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-64px)] bg-gray-100">
      {/* Services Sidebar */}
      <div className="w-80 bg-white shadow-lg border-r border-gray-200">
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-800">Available Services</h2>
          <p className="text-sm text-gray-600 mt-1">Click to execute or ask Alith about them</p>
        </div>
        
        <div className="p-4">
          <div className="space-y-3">
            {services.map((service) => (
              <div
                key={service.id}
                className="p-3 border border-gray-200 rounded-lg hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => executeService(service.id)}
              >
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium text-gray-800">{service.name}</h3>
                  <span
                    className={`px-2 py-1 text-xs rounded-full ${
                      service.status === 'active'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-600'
                    }`}
                  >
                    {service.status}
                  </span>
                </div>
                <p className="text-sm text-gray-600">{service.description}</p>
              </div>
            ))}
          </div>
          
          {/* Placeholder for more services */}
          <div className="mt-6 p-4 border-2 border-dashed border-gray-300 rounded-lg text-center text-gray-500">
            <p className="text-sm">More services coming soon...</p>
            <p className="text-xs mt-1">Space reserved for additional services</p>
          </div>
        </div>
      </div>

      {/* Chat Interface */}
      <div className="flex-1 flex flex-col">
        {/* Chat Header */}
        <div className="bg-white shadow-sm border-b border-gray-200 p-4">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold mr-3">
              A
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-800">Alith AI Assistant</h1>
              <p className="text-sm text-gray-600">Metis Blockchain AI • Playground Environment</p>
            </div>
          </div>
        </div>

        {/* Messages Container */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${
                message.sender === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.sender === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white shadow border border-gray-200'
                }`}
              >
                <p className="text-sm">{message.content}</p>
                <p
                  className={`text-xs mt-1 ${
                    message.sender === 'user' ? 'text-blue-100' : 'text-gray-500'
                  }`}
                >
                  {message.timestamp.toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white shadow border border-gray-200 rounded-lg px-4 py-2">
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                  <span className="text-sm text-gray-600">Alith is thinking...</span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Message Input */}
        <div className="bg-white border-t border-gray-200 p-4">
          <div className="flex space-x-4">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask Alith anything or request a service..."
              className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isLoading}
            />
            <button
              onClick={sendMessage}
              disabled={isLoading || !inputMessage.trim()}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-6 py-2 rounded-lg font-medium transition-colors"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
