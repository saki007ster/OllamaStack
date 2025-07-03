# 🔧 OllamaStack Customization Guide

This comprehensive guide will help you customize and extend every component of OllamaStack for your specific needs.

## Table of Contents

- [Frontend Customization](#frontend-customization)
- [Backend Customization](#backend-customization)
- [LLM & Agent Customization](#llm--agent-customization)
- [UI/UX Customization](#uiux-customization)
- [Configuration Management](#configuration-management)
- [Adding New Features](#adding-new-features)
- [Integration Examples](#integration-examples)

## Frontend Customization

### 🎨 Styling & Themes

#### Customizing Colors

Edit `frontend/tailwind.config.js` to change the color scheme:

```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        // Your custom colors
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          900: '#1e3a8a',
        },
        // Add brand colors
        brand: {
          light: '#your-color',
          DEFAULT: '#your-color',
          dark: '#your-color',
        }
      }
    }
  }
}
```

#### Custom CSS Classes

Add custom styles in `frontend/styles/globals.css`:

```css
/* Custom gradient backgrounds */
.gradient-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Custom animations */
@keyframes pulse-slow {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.8; }
}

.animate-pulse-slow {
  animation: pulse-slow 3s ease-in-out infinite;
}

/* Dark mode support */
.dark .custom-bg {
  background-color: #1a1a1a;
}
```

### 🧩 Component Customization

#### Modifying the Chat Interface

**Location**: `frontend/components/ChatInterface.tsx`

```typescript
// Example: Add custom message types
interface CustomMessage extends UIMessage {
  messageType?: 'text' | 'image' | 'code' | 'file';
  metadata?: {
    attachments?: File[];
    reactions?: string[];
    priority?: 'low' | 'normal' | 'high';
  };
}

// Example: Custom message renderer
const renderCustomMessage = (message: CustomMessage) => {
  switch (message.messageType) {
    case 'image':
      return <ImageMessage message={message} />;
    case 'code':
      return <CodeMessage message={message} />;
    case 'file':
      return <FileMessage message={message} />;
    default:
      return <TextMessage message={message} />;
  }
};
```

#### Creating Custom Components

**New Component**: `frontend/components/CustomWidget.tsx`

```typescript
import React from 'react';

interface CustomWidgetProps {
  title: string;
  data: any[];
  onAction?: (action: string) => void;
}

export const CustomWidget: React.FC<CustomWidgetProps> = ({ 
  title, 
  data, 
  onAction 
}) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold mb-4">{title}</h3>
      <div className="space-y-2">
        {data.map((item, index) => (
          <div key={index} className="flex justify-between items-center">
            <span>{item.label}</span>
            <button 
              onClick={() => onAction?.(item.action)}
              className="px-3 py-1 bg-primary-500 text-white rounded"
            >
              {item.buttonText}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};
```

#### Modifying the Sidebar

**Location**: `frontend/components/Sidebar.tsx`

```typescript
// Add custom sidebar sections
const CustomSidebarSection = () => (
  <div className="p-4 border-t border-gray-700">
    <h4 className="text-sm font-medium text-gray-300 mb-3">Quick Actions</h4>
    <div className="space-y-2">
      <button className="w-full text-left px-3 py-2 text-sm text-gray-300 hover:bg-gray-700 rounded">
        📊 Analytics
      </button>
      <button className="w-full text-left px-3 py-2 text-sm text-gray-300 hover:bg-gray-700 rounded">
        ⚙️ Settings
      </button>
      <button className="w-full text-left px-3 py-2 text-sm text-gray-300 hover:bg-gray-700 rounded">
        🔗 Integrations
      </button>
    </div>
  </div>
);
```

### 🔧 API Client Customization

**Location**: `frontend/lib/api.ts`

```typescript
// Add custom API endpoints
class CustomApiClient extends ApiClient {
  // Custom analytics endpoint
  async getAnalytics(timeRange: string) {
    return this.client.get(`/analytics?range=${timeRange}`);
  }

  // Custom file upload
  async uploadFile(file: File, metadata: any) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('metadata', JSON.stringify(metadata));
    
    return this.client.post('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  }

  // Custom webhook handler
  async registerWebhook(url: string, events: string[]) {
    return this.client.post('/webhooks', { url, events });
  }
}
```

## Backend Customization

### 🛠️ API Endpoints

#### Adding Custom Routes

**New File**: `backend/app/routes/custom.py`

```python
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import asyncio

router = APIRouter(prefix="/api/v1/custom", tags=["custom"])

# Custom models
class CustomRequest(BaseModel):
    action: str
    parameters: dict
    user_id: Optional[str] = None

class CustomResponse(BaseModel):
    success: bool
    data: dict
    message: str

@router.post("/action", response_model=CustomResponse)
async def execute_custom_action(request: CustomRequest):
    """Execute a custom action with parameters."""
    try:
        # Your custom logic here
        result = await process_custom_action(
            request.action, 
            request.parameters,
            request.user_id
        )
        
        return CustomResponse(
            success=True,
            data=result,
            message="Action executed successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/analytics")
async def get_analytics(
    timeframe: str = "7d",
    metric: str = "all"
):
    """Get custom analytics data."""
    analytics_data = await calculate_analytics(timeframe, metric)
    return analytics_data
```

#### Custom Middleware

**Location**: `backend/app/main.py`

```python
from fastapi import Request, Response
import time
import logging

@app.middleware("http")
async def custom_middleware(request: Request, call_next):
    # Custom request logging
    start_time = time.time()
    user_agent = request.headers.get("user-agent")
    
    # Process request
    response = await call_next(request)
    
    # Custom response headers
    response.headers["X-Custom-Header"] = "OllamaStack-v1.0"
    response.headers["X-Response-Time"] = str(time.time() - start_time)
    
    # Log request details
    logger.info(f"Request: {request.method} {request.url} - "
               f"Status: {response.status_code} - "
               f"Time: {time.time() - start_time:.3f}s")
    
    return response
```

### 🤖 Custom LangChain Tools

**Location**: `backend/app/services/custom_tools.py`

```python
from langchain.tools import Tool
from langchain.tools.base import BaseTool
from typing import Optional, Type
from pydantic import BaseModel, Field
import requests
import json

class WeatherToolInput(BaseModel):
    location: str = Field(description="City name or coordinates")
    units: str = Field(default="metric", description="Temperature units")

class WeatherTool(BaseTool):
    name = "weather"
    description = "Get current weather for a location"
    args_schema: Type[BaseModel] = WeatherToolInput

    def _run(self, location: str, units: str = "metric") -> str:
        """Get weather data for location."""
        try:
            # Replace with your weather API
            api_key = "your-weather-api-key"
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": location,
                "appid": api_key,
                "units": units
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            return f"Weather in {location}: {data['weather'][0]['description']}, "
                   f"Temperature: {data['main']['temp']}°"
        except Exception as e:
            return f"Error getting weather: {str(e)}"

    async def _arun(self, location: str, units: str = "metric") -> str:
        """Async version of weather tool."""
        return self._run(location, units)

# Database query tool
class DatabaseTool(BaseTool):
    name = "database_query"
    description = "Query the application database"
    
    def _run(self, query: str) -> str:
        """Execute a safe database query."""
        # Add your database query logic
        # Make sure to sanitize inputs!
        try:
            # Example with SQLAlchemy
            from sqlalchemy import text
            
            # Only allow SELECT queries for safety
            if not query.strip().upper().startswith("SELECT"):
                return "Only SELECT queries are allowed"
            
            # Execute query and return results
            # results = db.execute(text(query)).fetchall()
            # return json.dumps([dict(row) for row in results])
            
            return "Database query executed successfully"
        except Exception as e:
            return f"Database error: {str(e)}"
```

### 📊 Custom Services

**New File**: `backend/app/services/analytics.py`

```python
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio
from collections import defaultdict

class AnalyticsService:
    def __init__(self):
        self.metrics_storage = defaultdict(list)
    
    async def track_event(
        self, 
        event_type: str, 
        user_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """Track custom events."""
        event = {
            "timestamp": datetime.utcnow(),
            "event_type": event_type,
            "user_id": user_id,
            "metadata": metadata or {}
        }
        self.metrics_storage[event_type].append(event)
    
    async def get_metrics(
        self, 
        timeframe: str = "7d",
        event_types: Optional[List[str]] = None
    ) -> Dict:
        """Get analytics metrics."""
        # Calculate date range
        end_date = datetime.utcnow()
        if timeframe == "24h":
            start_date = end_date - timedelta(hours=24)
        elif timeframe == "7d":
            start_date = end_date - timedelta(days=7)
        elif timeframe == "30d":
            start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=7)
        
        # Filter events by timeframe
        filtered_events = {}
        for event_type, events in self.metrics_storage.items():
            if event_types and event_type not in event_types:
                continue
            
            filtered_events[event_type] = [
                event for event in events
                if start_date <= event["timestamp"] <= end_date
            ]
        
        # Calculate metrics
        metrics = {
            "total_events": sum(len(events) for events in filtered_events.values()),
            "event_breakdown": {
                event_type: len(events) 
                for event_type, events in filtered_events.items()
            },
            "timeframe": timeframe,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
        
        return metrics

# Initialize analytics service
analytics_service = AnalyticsService()
```

## LLM & Agent Customization

### 🧠 Custom Agent Configuration

**Location**: `backend/app/services/langchain_agent.py`

```python
from langchain.agents import create_react_agent
from langchain.prompts import PromptTemplate

# Custom agent prompt
CUSTOM_AGENT_PROMPT = PromptTemplate.from_template("""
You are an AI assistant specialized in {domain}. 

Your expertise includes:
{expertise_areas}

Current conversation context:
{context}

Available tools:
{tools}

User: {input}
{agent_scratchpad}

Remember to:
1. Be helpful and accurate
2. Use tools when appropriate
3. Explain your reasoning
4. Ask for clarification if needed
""")

# Custom agent with specialized tools
def create_custom_agent(domain: str, expertise_areas: List[str]):
    """Create a specialized agent for a specific domain."""
    
    # Select relevant tools based on domain
    domain_tools = get_domain_specific_tools(domain)
    
    # Create custom agent
    agent = create_react_agent(
        llm=OllamaLLM(model="llama3.2"),
        tools=domain_tools,
        prompt=CUSTOM_AGENT_PROMPT
    )
    
    return agent

def get_domain_specific_tools(domain: str) -> List[Tool]:
    """Get tools specific to a domain."""
    base_tools = [calculator_tool, timestamp_tool]
    
    if domain == "data_analysis":
        base_tools.extend([
            data_visualization_tool,
            statistical_analysis_tool,
            csv_reader_tool
        ])
    elif domain == "web_development":
        base_tools.extend([
            code_formatter_tool,
            package_search_tool,
            documentation_tool
        ])
    elif domain == "customer_support":
        base_tools.extend([
            ticket_lookup_tool,
            knowledge_base_tool,
            escalation_tool
        ])
    
    return base_tools
```

### 🎯 Custom Model Configuration

```python
# Custom model configurations
CUSTOM_MODEL_CONFIGS = {
    "creative_writer": {
        "model": "llama3.2",
        "temperature": 0.9,
        "max_tokens": 2000,
        "system_prompt": "You are a creative writing assistant..."
    },
    "code_assistant": {
        "model": "codellama",
        "temperature": 0.1,
        "max_tokens": 1500,
        "system_prompt": "You are a coding assistant..."
    },
    "data_analyst": {
        "model": "llama3.2",
        "temperature": 0.3,
        "max_tokens": 1000,
        "system_prompt": "You are a data analysis expert..."
    }
}

def get_specialized_llm(assistant_type: str) -> OllamaLLM:
    """Get a specialized LLM configuration."""
    config = CUSTOM_MODEL_CONFIGS.get(assistant_type, CUSTOM_MODEL_CONFIGS["creative_writer"])
    
    return OllamaLLM(
        model=config["model"],
        temperature=config["temperature"],
        max_tokens=config["max_tokens"],
        system=config["system_prompt"]
    )
```

## UI/UX Customization

### 🎨 Custom Themes

**Location**: `frontend/lib/themes.ts`

```typescript
// Theme definitions
export const themes = {
  light: {
    name: 'Light',
    colors: {
      primary: '#3b82f6',
      background: '#ffffff',
      surface: '#f8fafc',
      text: '#1f2937',
      textSecondary: '#6b7280',
      border: '#e5e7eb',
    }
  },
  dark: {
    name: 'Dark',
    colors: {
      primary: '#3b82f6',
      background: '#0f172a',
      surface: '#1e293b',
      text: '#f1f5f9',
      textSecondary: '#94a3b8',
      border: '#334155',
    }
  },
  custom: {
    name: 'Custom Brand',
    colors: {
      primary: '#your-brand-color',
      background: '#your-bg-color',
      surface: '#your-surface-color',
      text: '#your-text-color',
      textSecondary: '#your-secondary-text',
      border: '#your-border-color',
    }
  }
};

// Theme context
export const ThemeContext = createContext({
  theme: themes.light,
  setTheme: (theme: Theme) => {},
});

// Theme provider component
export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentTheme, setCurrentTheme] = useState(themes.light);
  
  return (
    <ThemeContext.Provider value={{ theme: currentTheme, setTheme: setCurrentTheme }}>
      <div className={`theme-${currentTheme.name.toLowerCase()}`}>
        {children}
      </div>
    </ThemeContext.Provider>
  );
};
```

### 🖼️ Custom Layout Options

```typescript
// Layout configurations
export const layoutConfigs = {
  sidebar: {
    width: 280,
    collapsible: true,
    position: 'left' | 'right',
    style: 'modern' | 'classic' | 'minimal'
  },
  header: {
    height: 64,
    fixed: true,
    showLogo: true,
    showUserMenu: true
  },
  chatArea: {
    maxWidth: 800,
    showTimestamps: true,
    bubbleStyle: 'modern' | 'classic' | 'minimal'
  }
};

// Layout component
export const CustomLayout: React.FC<LayoutProps> = ({ 
  config = layoutConfigs,
  children 
}) => {
  return (
    <div className="flex h-screen">
      {config.sidebar.position === 'left' && (
        <Sidebar 
          width={config.sidebar.width}
          style={config.sidebar.style}
          collapsible={config.sidebar.collapsible}
        />
      )}
      
      <div className="flex-1 flex flex-col">
        <Header 
          height={config.header.height}
          fixed={config.header.fixed}
          showLogo={config.header.showLogo}
        />
        
        <main className="flex-1">
          {children}
        </main>
      </div>
      
      {config.sidebar.position === 'right' && (
        <Sidebar 
          width={config.sidebar.width}
          style={config.sidebar.style}
          collapsible={config.sidebar.collapsible}
        />
      )}
    </div>
  );
};
```

## Configuration Management

### ⚙️ Environment Configuration

**Location**: `backend/app/config.py`

```python
from pydantic_settings import BaseSettings
from typing import Dict, Any, Optional

class CustomSettings(BaseSettings):
    """Extended settings for custom features."""
    
    # Custom feature flags
    enable_analytics: bool = True
    enable_file_upload: bool = False
    enable_webhooks: bool = False
    enable_custom_tools: bool = True
    
    # Custom integrations
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    weather_api_key: Optional[str] = None
    
    # Database settings
    database_url: Optional[str] = None
    redis_url: Optional[str] = None
    
    # Custom model configurations
    custom_models: Dict[str, Any] = {
        "default": {
            "model": "llama3.2",
            "temperature": 0.7,
            "max_tokens": 1000
        }
    }
    
    # Rate limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    
    # File upload limits
    max_file_size_mb: int = 10
    allowed_file_types: list = [".txt", ".pdf", ".docx", ".md"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Usage in your app
settings = CustomSettings()
```

### 🔧 Runtime Configuration

```python
# Configuration manager
class ConfigManager:
    def __init__(self):
        self.configs = {}
        self.load_default_configs()
    
    def load_default_configs(self):
        """Load default configurations."""
        self.configs = {
            "ui": {
                "theme": "light",
                "sidebar_width": 280,
                "show_timestamps": True
            },
            "ai": {
                "default_model": "llama3.2",
                "temperature": 0.7,
                "max_history": 10
            },
            "features": {
                "analytics": True,
                "file_upload": False,
                "webhooks": False
            }
        }
    
    def get_config(self, key: str, default=None):
        """Get configuration value."""
        keys = key.split(".")
        value = self.configs
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set_config(self, key: str, value):
        """Set configuration value."""
        keys = key.split(".")
        config = self.configs
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save_configs(self):
        """Save configurations to file."""
        import json
        with open("config.json", "w") as f:
            json.dump(self.configs, f, indent=2)

# Global config manager
config_manager = ConfigManager()
```

## Adding New Features

### 📱 Adding File Upload Feature

**Frontend Component**: `frontend/components/FileUpload.tsx`

```typescript
import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';

interface FileUploadProps {
  onFileUpload: (files: File[]) => void;
  maxFiles?: number;
  acceptedTypes?: string[];
}

export const FileUpload: React.FC<FileUploadProps> = ({
  onFileUpload,
  maxFiles = 5,
  acceptedTypes = ['.txt', '.pdf', '.docx', '.md']
}) => {
  const [uploading, setUploading] = useState(false);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    setUploading(true);
    try {
      await onFileUpload(acceptedFiles);
    } finally {
      setUploading(false);
    }
  }, [onFileUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    maxFiles,
    accept: acceptedTypes.reduce((acc, type) => {
      acc[`application/${type.slice(1)}`] = [type];
      return acc;
    }, {} as Record<string, string[]>)
  });

  return (
    <div
      {...getRootProps()}
      className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
        isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
      }`}
    >
      <input {...getInputProps()} />
      <div className="text-4xl mb-4">📎</div>
      {uploading ? (
        <div>
          <div className="animate-spin w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full mx-auto mb-2"></div>
          <p>Uploading files...</p>
        </div>
      ) : (
        <div>
          <p className="text-lg font-medium mb-2">
            {isDragActive ? 'Drop files here' : 'Drag files here or click to select'}
          </p>
          <p className="text-gray-500 text-sm">
            Supported: {acceptedTypes.join(', ')} (max {maxFiles} files)
          </p>
        </div>
      )}
    </div>
  );
};
```

**Backend Route**: `backend/app/routes/files.py`

```python
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import aiofiles
import os
from pathlib import Path

router = APIRouter(prefix="/api/v1/files", tags=["files"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload multiple files."""
    uploaded_files = []
    
    for file in files:
        # Validate file
        if file.size > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(400, f"File {file.filename} too large")
        
        # Save file
        file_path = UPLOAD_DIR / file.filename
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        uploaded_files.append({
            "filename": file.filename,
            "size": len(content),
            "path": str(file_path)
        })
    
    return {"uploaded_files": uploaded_files}

@router.get("/list")
async def list_files():
    """List uploaded files."""
    files = []
    for file_path in UPLOAD_DIR.iterdir():
        if file_path.is_file():
            files.append({
                "filename": file_path.name,
                "size": file_path.stat().st_size,
                "modified": file_path.stat().st_mtime
            })
    
    return {"files": files}
```

### 📊 Adding Analytics Dashboard

**Frontend Component**: `frontend/components/Analytics.tsx`

```typescript
import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api';

interface AnalyticsData {
  totalMessages: number;
  totalConversations: number;
  averageResponseTime: number;
  topModels: Array<{ name: string; usage: number }>;
}

export const Analytics: React.FC = () => {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      const response = await api.get('/analytics');
      setData(response.data);
    } catch (error) {
      console.error('Failed to load analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="animate-pulse">Loading analytics...</div>;
  }

  if (!data) {
    return <div>Failed to load analytics</div>;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-sm font-medium text-gray-500">Total Messages</h3>
        <p className="text-3xl font-bold text-gray-900">{data.totalMessages}</p>
      </div>
      
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-sm font-medium text-gray-500">Conversations</h3>
        <p className="text-3xl font-bold text-gray-900">{data.totalConversations}</p>
      </div>
      
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-sm font-medium text-gray-500">Avg Response Time</h3>
        <p className="text-3xl font-bold text-gray-900">{data.averageResponseTime}s</p>
      </div>
      
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-sm font-medium text-gray-500 mb-4">Top Models</h3>
        <div className="space-y-2">
          {data.topModels.map((model, index) => (
            <div key={index} className="flex justify-between">
              <span className="text-sm">{model.name}</span>
              <span className="text-sm font-medium">{model.usage}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
```

## Integration Examples

### 🔗 Database Integration

```python
# SQLAlchemy integration
from sqlalchemy import create_engine, Column, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True)
    title = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True)
    conversation_id = Column(String)
    role = Column(String(20))
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Database service
class DatabaseService:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
    
    async def save_conversation(self, conversation_data: dict):
        """Save conversation to database."""
        session = self.SessionLocal()
        try:
            conversation = Conversation(**conversation_data)
            session.add(conversation)
            session.commit()
            return conversation.id
        finally:
            session.close()
    
    async def get_conversations(self, limit: int = 50):
        """Get recent conversations."""
        session = self.SessionLocal()
        try:
            conversations = session.query(Conversation)\
                .order_by(Conversation.updated_at.desc())\
                .limit(limit)\
                .all()
            return [
                {
                    "id": conv.id,
                    "title": conv.title,
                    "created_at": conv.created_at.isoformat(),
                    "updated_at": conv.updated_at.isoformat()
                }
                for conv in conversations
            ]
        finally:
            session.close()
```

### 🔔 Webhook Integration

```python
# Webhook service
import httpx
from typing import Dict, List

class WebhookService:
    def __init__(self):
        self.webhooks: Dict[str, List[str]] = {}
    
    async def register_webhook(self, event_type: str, url: str):
        """Register a webhook for an event type."""
        if event_type not in self.webhooks:
            self.webhooks[event_type] = []
        
        if url not in self.webhooks[event_type]:
            self.webhooks[event_type].append(url)
    
    async def trigger_webhook(self, event_type: str, data: Dict):
        """Trigger webhooks for an event."""
        if event_type not in self.webhooks:
            return
        
        async with httpx.AsyncClient() as client:
            for url in self.webhooks[event_type]:
                try:
                    await client.post(
                        url,
                        json={
                            "event_type": event_type,
                            "data": data,
                            "timestamp": datetime.utcnow().isoformat()
                        },
                        timeout=10.0
                    )
                except Exception as e:
                    logger.error(f"Webhook failed {url}: {e}")

# Usage in chat endpoint
@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    # ... existing chat logic ...
    
    # Trigger webhook
    await webhook_service.trigger_webhook("message_sent", {
        "conversation_id": request.conversation_id,
        "message": request.message,
        "response": response_text
    })
    
    return response
```

### 🔍 Search Integration

```python
# Search service with vector embeddings
import numpy as np
from sentence_transformers import SentenceTransformer

class SearchService:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.documents = []
        self.embeddings = []
    
    async def index_document(self, doc_id: str, content: str, metadata: dict = None):
        """Index a document for search."""
        embedding = self.model.encode(content)
        
        self.documents.append({
            "id": doc_id,
            "content": content,
            "metadata": metadata or {},
            "embedding": embedding
        })
        
        self.embeddings.append(embedding)
    
    async def search(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for documents similar to query."""
        if not self.documents:
            return []
        
        query_embedding = self.model.encode(query)
        
        # Calculate cosine similarity
        similarities = np.dot(self.embeddings, query_embedding) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # Get top results
        top_indices = np.argsort(similarities)[::-1][:limit]
        
        results = []
        for idx in top_indices:
            doc = self.documents[idx]
            results.append({
                "id": doc["id"],
                "content": doc["content"],
                "metadata": doc["metadata"],
                "similarity": float(similarities[idx])
            })
        
        return results

# Search endpoint
@router.get("/search")
async def search_documents(query: str, limit: int = 10):
    """Search indexed documents."""
    results = await search_service.search(query, limit)
    return {"query": query, "results": results}
```

## Best Practices

### 🛡️ Security Considerations

1. **Input Validation**: Always validate and sanitize user inputs
2. **Rate Limiting**: Implement rate limiting for API endpoints
3. **Authentication**: Add proper authentication and authorization
4. **CORS**: Configure CORS properly for production
5. **Environment Variables**: Never commit secrets to version control

### 🚀 Performance Optimization

1. **Caching**: Implement Redis caching for frequently accessed data
2. **Connection Pooling**: Use connection pooling for databases
3. **Async Operations**: Use async/await for I/O operations
4. **Code Splitting**: Implement code splitting in frontend
5. **CDN**: Use CDN for static assets in production

### 📝 Development Workflow

1. **Branch Strategy**: Use feature branches for development
2. **Code Review**: Implement mandatory code reviews
3. **Testing**: Write comprehensive tests for new features
4. **Documentation**: Update documentation for any changes
5. **Deployment**: Use CI/CD for automated deployments

---

This guide provides a comprehensive overview of how to customize every aspect of OllamaStack. For specific implementation questions, refer to the existing codebase or create an issue on GitHub. 