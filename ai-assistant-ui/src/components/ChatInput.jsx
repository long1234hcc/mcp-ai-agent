import React, { useState } from 'react';
import { FaPaperPlane } from 'react-icons/fa';

const ChatInput = ({ onSendMessage, isLoading, planningMode, onTogglePlanning }) => {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input);
      setInput('');
    }
  };

  return (
    <div className="border-t bg-white p-4">
      {/* Planning Mode Toggle */}
      <div className="mb-3 flex items-center gap-2">
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={planningMode}
            onChange={(e) => onTogglePlanning(e.target.checked)}
            className="w-4 h-4 text-purple-600 rounded focus:ring-2 focus:ring-purple-500"
          />
          <span className="text-sm text-gray-700">
            Planning Mode {planningMode ? '🧠' : '⚡'}
          </span>
        </label>
        <span className="text-xs text-gray-500">
          {planningMode ? '(For complex tasks)' : '(Fast reactive mode)'}
        </span>
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          disabled={isLoading}
          className="flex-1 px-4 py-3 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
        />
        <button
          type="submit"
          disabled={isLoading || !input.trim()}
          className="bg-blue-500 text-white px-6 py-3 rounded-full hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
        >
          <FaPaperPlane />
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  );
};

export default ChatInput;
