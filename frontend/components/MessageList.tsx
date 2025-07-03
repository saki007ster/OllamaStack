import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/cjs/styles/prism';
import { UIMessage } from '@/types';

interface MessageListProps {
  messages: UIMessage[];
  showTimestamps?: boolean;
}

interface MessageItemProps {
  message: UIMessage;
  showTimestamp?: boolean;
}

function MessageItem({ message, showTimestamp }: MessageItemProps) {
  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';

  return (
    <div className={`mb-6 flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[80%] rounded-lg px-4 py-3 ${
          isUser
            ? 'message-user'
            : isSystem
            ? 'message-system'
            : 'message-assistant'
        }`}
      >
        {/* Message content */}
        <div className="prose prose-sm max-w-none">
          {message.isLoading ? (
            <div className="flex items-center space-x-2">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
              <span className="text-gray-500 text-sm">AI is thinking...</span>
            </div>
          ) : (
            <ReactMarkdown>
              {message.content}
            </ReactMarkdown>
          )}
        </div>

        {/* Error indicator */}
        {message.error && (
          <div className="mt-2 text-xs text-red-500 flex items-center">
            <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            Error: {message.error}
          </div>
        )}

        {/* Timestamp */}
        {showTimestamp && (
          <div className={`mt-2 text-xs ${isUser ? 'text-white/70' : 'text-gray-500'}`}>
            {new Date(message.timestamp).toLocaleString()}
          </div>
        )}

        {/* Metadata */}
        {message.metadata && !message.isLoading && (
          <div className="mt-2 text-xs text-gray-400">
            Model: {message.metadata.model_used || 'Unknown'} | 
            Temp: {message.metadata.temperature || 0.7}
          </div>
        )}
      </div>
    </div>
  );
}

export default function MessageList({ messages, showTimestamps }: MessageListProps) {
  if (messages.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        <div className="text-center">
          <svg className="w-12 h-12 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          <p>No messages yet</p>
          <p className="text-sm">Start the conversation by typing a message below.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {messages.map((message) => (
        <MessageItem
          key={message.id}
          message={message}
          showTimestamp={showTimestamps}
        />
      ))}
    </div>
  );
} 