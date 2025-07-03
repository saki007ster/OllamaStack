import React, { useState } from 'react';
import { AppSettings } from '@/types';

interface HeaderProps {
  apiStatus: 'online' | 'offline' | 'checking';
  settings: AppSettings;
  onSettingsUpdate: (settings: Partial<AppSettings>) => void;
}

export default function Header({ apiStatus, settings, onSettingsUpdate }: HeaderProps) {
  const [showSettings, setShowSettings] = useState(false);

  const getStatusColor = () => {
    switch (apiStatus) {
      case 'online': return 'text-green-500';
      case 'offline': return 'text-red-500';
      case 'checking': return 'text-yellow-500';
      default: return 'text-gray-500';
    }
  };

  const getStatusIcon = () => {
    switch (apiStatus) {
      case 'online': return '●';
      case 'offline': return '●';
      case 'checking': return '⟳';
      default: return '●';
    }
  };

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h1 className="text-xl font-semibold text-gray-900">AI Assistant</h1>
          <div className="flex items-center space-x-2 text-sm">
            <span className={`${getStatusColor()}`}>
              {getStatusIcon()}
            </span>
            <span className="text-gray-600 capitalize">{apiStatus}</span>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            title="Settings"
          >
            <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </button>
        </div>
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <div className="absolute right-6 top-16 w-80 bg-white border border-gray-200 rounded-lg shadow-lg z-50 p-4">
          <div className="space-y-4">
            <h3 className="font-medium text-gray-900">Settings</h3>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Temperature
              </label>
              <input
                type="range"
                min="0"
                max="2"
                step="0.1"
                value={settings.temperature}
                onChange={(e) => onSettingsUpdate({ temperature: parseFloat(e.target.value) })}
                className="w-full"
              />
              <div className="text-xs text-gray-500 mt-1">{settings.temperature}</div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Max Tokens
              </label>
              <input
                type="number"
                min="1"
                max="4000"
                value={settings.maxTokens}
                onChange={(e) => onSettingsUpdate({ maxTokens: parseInt(e.target.value) })}
                className="input w-full"
              />
            </div>

            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-gray-700">
                Show Timestamps
              </label>
              <input
                type="checkbox"
                checked={settings.showTimestamps}
                onChange={(e) => onSettingsUpdate({ showTimestamps: e.target.checked })}
                className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
            </div>

            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-gray-700">
                Auto Scroll
              </label>
              <input
                type="checkbox"
                checked={settings.autoScroll}
                onChange={(e) => onSettingsUpdate({ autoScroll: e.target.checked })}
                className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
            </div>

            <button
              onClick={() => setShowSettings(false)}
              className="w-full btn btn-outline"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </header>
  );
} 