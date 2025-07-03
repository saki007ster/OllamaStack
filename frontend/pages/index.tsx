import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { Toaster } from 'react-hot-toast';
import ChatInterface from '@/components/ChatInterface';
import Sidebar from '@/components/Sidebar';
import Header from '@/components/Header';
import StatusBar from '@/components/StatusBar';
import { api } from '@/lib/api';
import { AppState, ConversationState, UIMessage, AppSettings } from '@/types';
import { v4 as uuidv4 } from 'uuid';

const defaultSettings: AppSettings = {
  apiUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  defaultModel: 'llama3',
  temperature: 0.7,
  maxTokens: 1000,
  theme: 'light',
  autoScroll: true,
  showTimestamps: false,
  enableSound: false,
};

export default function Home() {
  const [appState, setAppState] = useState<AppState>({
    isLoading: false,
    error: null,
    currentConversation: null,
    conversations: {},
    settings: defaultSettings,
  });

  const [apiStatus, setApiStatus] = useState<'online' | 'offline' | 'checking'>('checking');

  // Check API status on mount
  useEffect(() => {
    checkApiStatus();
    const interval = setInterval(checkApiStatus, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  // Load saved state from localStorage
  useEffect(() => {
    const savedState = localStorage.getItem('ollamastack-state');
    if (savedState) {
      try {
        const parsed = JSON.parse(savedState);
        setAppState(prev => ({
          ...prev,
          conversations: parsed.conversations || {},
          currentConversation: parsed.currentConversation || null,
          settings: { ...defaultSettings, ...parsed.settings },
        }));
      } catch (error) {
        console.error('Failed to load saved state:', error);
      }
    }
  }, []);

  // Save state to localStorage
  useEffect(() => {
    const stateToSave = {
      conversations: appState.conversations,
      currentConversation: appState.currentConversation,
      settings: appState.settings,
    };
    localStorage.setItem('ollamastack-state', JSON.stringify(stateToSave));
  }, [appState.conversations, appState.currentConversation, appState.settings]);

  const checkApiStatus = async () => {
    try {
      const isOnline = await api.testConnection();
      setApiStatus(isOnline ? 'online' : 'offline');
    } catch {
      setApiStatus('offline');
    }
  };

  const createNewConversation = (): string => {
    const id = uuidv4();
    const newConversation: ConversationState = {
      id,
      messages: [],
      isLoading: false,
      title: 'New Conversation',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    setAppState(prev => ({
      ...prev,
      conversations: {
        ...prev.conversations,
        [id]: newConversation,
      },
      currentConversation: id,
    }));

    return id;
  };

  const selectConversation = (id: string) => {
    setAppState(prev => ({
      ...prev,
      currentConversation: id,
    }));
  };

  const deleteConversation = (id: string) => {
    setAppState(prev => {
      const newConversations = { ...prev.conversations };
      delete newConversations[id];
      
      return {
        ...prev,
        conversations: newConversations,
        currentConversation: prev.currentConversation === id ? null : prev.currentConversation,
      };
    });
  };

  const sendMessage = async (content: string) => {
    let conversationId = appState.currentConversation;
    
    // Create new conversation if none exists
    if (!conversationId) {
      conversationId = createNewConversation();
    }

    const messageId = uuidv4();
    const userMessage: UIMessage = {
      id: messageId,
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
    };

    // Add user message
    setAppState(prev => ({
      ...prev,
      conversations: {
        ...prev.conversations,
        [conversationId!]: {
          ...prev.conversations[conversationId!],
          messages: [...prev.conversations[conversationId!].messages, userMessage],
          updatedAt: new Date().toISOString(),
          title: prev.conversations[conversationId!].messages.length === 0 
            ? content.slice(0, 50) + (content.length > 50 ? '...' : '')
            : prev.conversations[conversationId!].title,
        },
      },
    }));

    // Add loading message
    const loadingMessageId = uuidv4();
    const loadingMessage: UIMessage = {
      id: loadingMessageId,
      role: 'assistant',
      content: '',
      timestamp: new Date().toISOString(),
      isLoading: true,
    };

    setAppState(prev => ({
      ...prev,
      conversations: {
        ...prev.conversations,
        [conversationId!]: {
          ...prev.conversations[conversationId!],
          messages: [...prev.conversations[conversationId!].messages, loadingMessage],
        },
      },
    }));

    try {
      const response = await api.chat({
        message: content,
        conversation_id: conversationId,
        temperature: appState.settings.temperature,
        max_tokens: appState.settings.maxTokens,
      });

      // Replace loading message with response
      setAppState(prev => ({
        ...prev,
        conversations: {
          ...prev.conversations,
          [conversationId!]: {
            ...prev.conversations[conversationId!],
            messages: prev.conversations[conversationId!].messages.map(msg =>
              msg.id === loadingMessageId
                ? {
                    ...msg,
                    content: response.message,
                    isLoading: false,
                    metadata: response.metadata,
                  }
                : msg
            ),
            updatedAt: new Date().toISOString(),
          },
        },
      }));
    } catch (error) {
      // Replace loading message with error
      setAppState(prev => ({
        ...prev,
        conversations: {
          ...prev.conversations,
          [conversationId!]: {
            ...prev.conversations[conversationId!],
            messages: prev.conversations[conversationId!].messages.map(msg =>
              msg.id === loadingMessageId
                ? {
                    ...msg,
                    content: 'Sorry, I encountered an error processing your message.',
                    isLoading: false,
                    error: error instanceof Error ? error.message : 'Unknown error',
                  }
                : msg
            ),
          },
        },
      }));
    }
  };

  const updateSettings = (newSettings: Partial<AppSettings>) => {
    setAppState(prev => ({
      ...prev,
      settings: {
        ...prev.settings,
        ...newSettings,
      },
    }));
  };

  const currentConversation = appState.currentConversation 
    ? appState.conversations[appState.currentConversation]
    : null;

  return (
    <>
      <Head>
        <title>OllamaStack - AI Chat Interface</title>
        <meta name="description" content="Modern AI chat interface powered by Ollama, LangChain, and FastAPI" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="flex h-screen bg-gray-50">
        {/* Sidebar */}
        <Sidebar
          conversations={Object.values(appState.conversations)}
          currentConversationId={appState.currentConversation}
          onSelect={selectConversation}
          onDelete={deleteConversation}
          onNew={createNewConversation}
        />

        {/* Main Content */}
        <div className="flex-1 flex flex-col">
          {/* Header */}
          <Header
            apiStatus={apiStatus}
            settings={appState.settings}
            onSettingsUpdate={updateSettings}
          />

          {/* Chat Interface */}
          <ChatInterface
            conversation={currentConversation}
            onSendMessage={sendMessage}
            settings={appState.settings}
          />

          {/* Status Bar */}
          <StatusBar
            apiStatus={apiStatus}
            conversationCount={Object.keys(appState.conversations).length}
            messageCount={currentConversation?.messages.length || 0}
          />
        </div>
      </div>

      {/* Toast notifications */}
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
        }}
      />
    </>
  );
} 