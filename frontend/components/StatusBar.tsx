import React from 'react';

interface StatusBarProps {
  apiStatus: 'online' | 'offline' | 'checking';
  conversationCount: number;
  messageCount: number;
}

export default function StatusBar({ apiStatus, conversationCount, messageCount }: StatusBarProps) {
  const statusColor = apiStatus === 'online' ? 'text-green-600' : apiStatus === 'offline' ? 'text-red-600' : 'text-yellow-600';
  const statusText = apiStatus === 'online' ? 'Connected' : apiStatus === 'offline' ? 'Disconnected' : 'Connecting...';

  return (
    <div className="bg-gray-100 border-t border-gray-200 px-4 py-2 flex items-center justify-between text-sm text-gray-600">
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full ${apiStatus === 'online' ? 'bg-green-500' : apiStatus === 'offline' ? 'bg-red-500' : 'bg-yellow-500'}`} />
          <span className={statusColor}>{statusText}</span>
        </div>
        
        <div className="flex items-center space-x-4">
          <span>Conversations: {conversationCount}</span>
          <span>Messages: {messageCount}</span>
        </div>
      </div>
      
      <div className="text-xs text-gray-500">
        OllamaStack v1.0.0
      </div>
    </div>
  );
} 