import React, { useState, useRef, useEffect } from 'react';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
import PlanSteps from './components/PlanSteps';
import { chatAPI } from './services/api';
import { FaCog } from 'react-icons/fa';

function App() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [planningMode, setPlanningMode] = useState(false);
  const [currentPlan, setCurrentPlan] = useState(null);
  const [sessionId] = useState('default_session');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (query) => {
    // Add user message
    const userMessage = { role: 'user', content: query };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setCurrentPlan(null);

    try {
      const response = await chatAPI.sendMessage(query, sessionId, planningMode);

      // Add assistant message
      const assistantMessage = {
        role: 'assistant',
        content: response.answer,
        tool_calls: response.steps || [],
      };
      setMessages((prev) => [...prev, assistantMessage]);

      // Display plan if available
      if (response.plan && response.plan.length > 0) {
        setCurrentPlan(response.plan);
      }
    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: `Error: ${error.response?.data?.detail || error.message}`,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm px-6 py-4 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
          <span>🤖</span> MCP AI Agent
        </h1>
        <div className="flex items-center gap-3 text-sm text-gray-600">
          <span className={`px-3 py-1 rounded-full ${planningMode ? 'bg-purple-100 text-purple-700' : 'bg-blue-100 text-blue-700'}`}>
            {planningMode ? '🧠 Planning' : '⚡ Reactive'}
          </span>
          <FaCog className="text-gray-400" />
        </div>
      </div>

      {/* Chat Container */}
      <div className="flex-1 overflow-y-auto px-6 py-4">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-gray-400">
              <p className="text-lg mb-2">👋 Welcome!</p>
              <p className="text-sm">Start a conversation with your AI Agent</p>
            </div>
          </div>
        )}

        {currentPlan && <PlanSteps steps={currentPlan} />}

        {messages.map((msg, index) => (
          <ChatMessage key={index} message={msg} />
        ))}

        {isLoading && (
          <div className="flex justify-start mb-4">
            <div className="bg-white rounded-2xl px-4 py-3 shadow-sm">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></span>
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></span>
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <ChatInput
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
        planningMode={planningMode}
        onTogglePlanning={setPlanningMode}
      />
    </div>
  );
}

export default App;
