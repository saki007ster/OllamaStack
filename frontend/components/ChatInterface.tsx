import React, { useRef, useEffect } from 'react';
import { ConversationState, UIMessage, AppSettings } from '@/types';
import MessageList from './MessageList';
import ChatInput from './ChatInput';

interface ChatInterfaceProps {
  conversation: ConversationState | null;
  onSendMessage: (message: string) => void;
  settings: AppSettings;
}

export default function ChatInterface({ conversation, onSendMessage, settings }: ChatInterfaceProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    if (settings.autoScroll) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversation?.messages, settings.autoScroll]);

  const isLoading = conversation?.messages.some(msg => msg.isLoading) || false;

  return (
    <div className="flex-1 flex flex-col bg-white">
      {conversation ? (
        <>
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4">
            <MessageList 
              messages={conversation.messages}
              showTimestamps={settings.showTimestamps}
            />
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="border-t border-gray-200 p-4">
            <ChatInput
              onSubmit={onSendMessage}
              isLoading={isLoading}
              placeholder="Type your message here..."
            />
          </div>
        </>
      ) : (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="w-16 h-16 mx-auto mb-4 bg-gradient-primary rounded-full flex items-center justify-center">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Welcome to OllamaStack
            </h3>
            <p className="text-gray-500 mb-4">
              Start a conversation with your AI assistant powered by Ollama and LangChain.
            </p>
            <p className="text-sm text-gray-400">
              Your conversations are saved locally and will persist between sessions.
            </p>
          </div>
        </div>
      )}
    </div>
  );
} 