import React from 'react';
import { FaUser, FaRobot, FaTools } from 'react-icons/fa';

const ChatMessage = ({ message }) => {
  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';

  if (isSystem) {
    return (
      <div className="flex justify-center my-2">
        <div className="bg-blue-50 text-blue-700 px-4 py-2 rounded-full text-sm">
          {message.content}
        </div>
      </div>
    );
  }

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`flex gap-3 max-w-[80%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        {/* Avatar */}
        <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
          isUser ? 'bg-blue-500' : 'bg-gray-700'
        }`}>
          {isUser ? (
            <FaUser className="text-white text-sm" />
          ) : (
            <FaRobot className="text-white text-sm" />
          )}
        </div>

        {/* Message Content */}
        <div className={`rounded-2xl px-4 py-3 ${
          isUser 
            ? 'bg-blue-500 text-white' 
            : 'bg-white text-gray-800 shadow-sm'
        }`}>
          <p className="whitespace-pre-wrap break-words">{message.content}</p>
          
          {/* Tool Calls Indicator */}
          {message.tool_calls && message.tool_calls.length > 0 && (
            <div className="mt-2 pt-2 border-t border-gray-200">
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <FaTools className="text-xs" />
                <span>Used {message.tool_calls.length} tool(s)</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;
