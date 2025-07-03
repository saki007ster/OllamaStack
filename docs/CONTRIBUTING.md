# 🤝 Contributing to OllamaStack

Thank you for your interest in contributing to OllamaStack! We're excited to have you join our community of developers building the future of privacy-first AI chat applications.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation Guidelines](#documentation-guidelines)
- [Pull Request Process](#pull-request-process)
- [Community & Support](#community--support)

## 🌟 Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](../CODE_OF_CONDUCT.md). We are committed to making participation in this project a harassment-free experience for everyone.

### Our Standards

- **Be respectful** and inclusive
- **Be collaborative** and constructive
- **Be patient** with new contributors
- **Be helpful** and share knowledge
- **Be open** to feedback and different perspectives

## 🚀 Getting Started

### Prerequisites

Before contributing, ensure you have:

- **Git** installed and configured
- **Docker** and **Docker Compose**
- **Node.js** 20+ and **npm**
- **Python** 3.11+
- Basic knowledge of **Next.js**, **FastAPI**, and **React**

### First-Time Contributors

If you're new to open source contribution:

1. 📚 Read our [Architecture Guide](./ARCHITECTURE.md) to understand the system
2. 🔍 Look for issues labeled `good first issue` or `help wanted`
3. 💬 Join our [Discord community](https://discord.gg/your-invite) for help
4. 📖 Review our [development workflow](#development-workflow)

## 🛠️ Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/yourusername/ollamastack.git
cd ollamastack

# Add upstream remote
git remote add upstream https://github.com/original-owner/ollamastack.git
```

### 2. Environment Setup

```bash
# Copy environment template
cp backend/env.example backend/.env

# Install all dependencies
npm run install:all

# Start development environment
docker-compose up -d ollama  # Start Ollama only
npm run dev:backend          # Terminal 1
npm run dev:frontend         # Terminal 2
```

### 3. Verify Setup

```bash
# Check if everything is working
curl http://localhost:8000/api/v1/health
curl http://localhost:3000

# Run tests
npm test
```

## 🎯 How to Contribute

### 🐛 Bug Reports

When reporting bugs, please include:

- **Clear description** of the issue
- **Steps to reproduce** the problem
- **Expected vs actual behavior**
- **Environment details** (OS, browser, versions)
- **Screenshots or logs** if applicable

**Bug Report Template:**

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g. macOS 12.0]
- Browser: [e.g. chrome 91.0]
- Node.js: [e.g. 20.0.0]
- Python: [e.g. 3.11.0]
```

### ✨ Feature Requests

For new features:

- **Check existing issues** to avoid duplicates
- **Explain the problem** you're solving
- **Describe your proposed solution**
- **Consider the impact** on existing users
- **Discuss implementation approach**

### 🔧 Code Contributions

#### Types of Contributions We Welcome:

| Category | Examples |
|----------|----------|
| **🐛 Bug Fixes** | Fixing broken functionality, edge cases |
| **✨ New Features** | New tools, UI components, API endpoints |
| **📚 Documentation** | Guides, API docs, code comments |
| **🎨 UI/UX** | Design improvements, accessibility |
| **⚡ Performance** | Optimization, caching, efficiency |
| **🧪 Testing** | Unit tests, integration tests, E2E |
| **🔧 DevOps** | CI/CD, Docker, deployment scripts |

## 📋 Development Workflow

### 1. Choose Your Work

```bash
# Look for issues
github issues list --label "good first issue"

# Or create a new feature proposal
# Discuss in GitHub Discussions first for major changes
```

### 2. Create a Branch

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/amazing-feature
# or
git checkout -b fix/important-bug
# or
git checkout -b docs/improve-readme
```

### 3. Development Cycle

```bash
# Make your changes
# ... code, code, code ...

# Test your changes
npm test
npm run lint
npm run type-check

# Commit frequently with good messages
git add .
git commit -m "feat: add amazing new feature

- Add new tool for text analysis
- Update API documentation
- Add comprehensive tests
"
```

### 4. Keep Updated

```bash
# Regularly sync with upstream
git fetch upstream
git rebase upstream/main
```

## 🎨 Coding Standards

### TypeScript/JavaScript

```typescript
// Use TypeScript interfaces for type safety
interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
}

// Use async/await over promises
async function sendMessage(message: string): Promise<ChatMessage> {
  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      body: JSON.stringify({ message }),
    });
    return await response.json();
  } catch (error) {
    console.error('Failed to send message:', error);
    throw error;
  }
}

// Use descriptive variable names
const userMessage = 'Hello, world!';
const assistantResponse = await sendMessage(userMessage);
```

### Python

```python
# Follow PEP 8 style guide
from typing import Optional, List
from pydantic import BaseModel

class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    conversation_id: Optional[str] = None
    temperature: float = 0.7

async def process_chat_request(
    request: ChatRequest,
    agent: Optional[Agent] = None
) -> ChatResponse:
    """Process a chat request and return response.
    
    Args:
        request: The chat request
        agent: Optional agent to use
        
    Returns:
        ChatResponse with the generated response
        
    Raises:
        ValueError: If request is invalid
    """
    if not request.message.strip():
        raise ValueError("Message cannot be empty")
    
    # Process the request
    response = await agent.invoke(request.message)
    
    return ChatResponse(
        content=response,
        conversation_id=request.conversation_id
    )
```

### React Components

```tsx
// Use functional components with TypeScript
interface MessageProps {
  message: ChatMessage;
  onReply?: (content: string) => void;
}

export const Message: React.FC<MessageProps> = ({ 
  message, 
  onReply 
}) => {
  const handleReply = useCallback((content: string) => {
    onReply?.(content);
  }, [onReply]);

  return (
    <div className={cn(
      "flex flex-col space-y-2 p-4 rounded-lg",
      message.role === 'user' 
        ? "bg-blue-50 ml-8" 
        : "bg-gray-50 mr-8"
    )}>
      <div className="text-sm text-gray-500">
        {message.role} • {formatTimestamp(message.timestamp)}
      </div>
      <div className="text-gray-900">
        <ReactMarkdown>{message.content}</ReactMarkdown>
      </div>
    </div>
  );
};
```

### File Naming Conventions

```
frontend/
├── components/
│   ├── ui/               # Reusable UI components
│   │   ├── Button.tsx
│   │   └── Input.tsx
│   ├── features/         # Feature-specific components
│   │   ├── chat/
│   │   └── settings/
│   └── layout/           # Layout components
├── lib/                  # Utilities
│   ├── api.ts           # API client
│   ├── utils.ts         # General utilities
│   └── types.ts         # Type definitions
└── styles/              # CSS files

backend/
├── app/
│   ├── api/             # API routes
│   │   ├── v1/
│   │   └── deps.py      # Dependencies
│   ├── core/            # Core functionality
│   │   ├── config.py
│   │   └── security.py
│   ├── models/          # Pydantic models
│   ├── services/        # Business logic
│   └── tools/           # LangChain tools
```

## 🧪 Testing Guidelines

### Frontend Testing

```typescript
// Component tests with React Testing Library
import { render, screen, fireEvent } from '@testing-library/react';
import { Message } from './Message';

describe('Message Component', () => {
  const mockMessage = {
    id: '1',
    content: 'Hello, world!',
    role: 'user' as const,
    timestamp: new Date(),
  };

  it('renders message content correctly', () => {
    render(<Message message={mockMessage} />);
    
    expect(screen.getByText('Hello, world!')).toBeInTheDocument();
    expect(screen.getByText('user')).toBeInTheDocument();
  });

  it('calls onReply when reply button is clicked', () => {
    const mockOnReply = jest.fn();
    render(<Message message={mockMessage} onReply={mockOnReply} />);
    
    const replyButton = screen.getByRole('button', { name: /reply/i });
    fireEvent.click(replyButton);
    
    expect(mockOnReply).toHaveBeenCalled();
  });
});
```

### Backend Testing

```python
# API tests with pytest and FastAPI TestClient
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestChatAPI:
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_chat_endpoint_valid_request(self):
        """Test chat endpoint with valid request."""
        request_data = {
            "message": "Hello, how are you?",
            "temperature": 0.7
        }
        
        response = client.post("/api/v1/chat", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "conversation_id" in data

    def test_chat_endpoint_invalid_request(self):
        """Test chat endpoint with invalid request."""
        request_data = {"message": ""}  # Empty message
        
        response = client.post("/api/v1/chat", json=request_data)
        
        assert response.status_code == 422
```

### Test Commands

```bash
# Run all tests
npm test

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode (during development)
npm run test:watch

# Run specific test files
npm test Message.test.tsx
pytest tests/test_chat_api.py

# Run tests for specific component
npm test -- --testNamePattern="Message"
```

## 📚 Documentation Guidelines

### Code Documentation

```python
def process_agent_request(
    message: str, 
    tools: List[Tool], 
    temperature: float = 0.7
) -> AgentResponse:
    """Process a request using an AI agent with tools.
    
    This function creates an agent with the provided tools and processes
    the user message to generate a response.
    
    Args:
        message: The user's input message
        tools: List of tools available to the agent
        temperature: Sampling temperature for response generation (0.0-2.0)
        
    Returns:
        AgentResponse containing the generated response and metadata
        
    Raises:
        ValueError: If message is empty or temperature is out of range
        AgentError: If agent processing fails
        
    Example:
        >>> tools = [calculator_tool, timestamp_tool]
        >>> response = process_agent_request(
        ...     "What's 2+2 and what time is it?", 
        ...     tools, 
        ...     0.7
        ... )
        >>> print(response.content)
    """
```

### README Updates

When adding new features, update relevant documentation:

- **Main README.md** - For major features
- **API Documentation** - For new endpoints
- **Customization Guide** - For new configuration options
- **Deployment Guide** - For new deployment methods

### Changelog

We follow [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
## [1.2.0] - 2024-01-15

### Added
- New text analysis tool for sentiment detection
- Support for custom model configurations
- Real-time typing indicators in chat

### Changed
- Improved error handling in API responses
- Updated Docker base images to latest versions

### Fixed
- Fixed memory leak in conversation management
- Resolved CORS issues in production deployment

### Deprecated
- Old authentication method (will be removed in 2.0.0)
```

## 🔄 Pull Request Process

### Before Submitting

- [ ] **Code is tested** - All tests pass
- [ ] **Code is documented** - Comments and docs updated
- [ ] **Code is formatted** - Passes linting
- [ ] **No breaking changes** - Or clearly documented
- [ ] **Commits are clean** - Squash if necessary

### PR Template

```markdown
## Description
Brief description of the changes.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Screenshots (if applicable)
Add screenshots to help explain your changes.

## Checklist
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally
```

### Review Process

1. **Automated Checks** - CI/CD pipeline runs
2. **Code Review** - Maintainers review your code
3. **Testing** - Manual testing if needed
4. **Approval** - At least one maintainer approval
5. **Merge** - Squash and merge to main

### Review Criteria

Reviewers will check:

- **Functionality** - Does it work as intended?
- **Code Quality** - Is it readable and maintainable?
- **Performance** - Any performance implications?
- **Security** - Any security concerns?
- **Documentation** - Is it properly documented?
- **Tests** - Are there adequate tests?

## 🏷️ Labels and Issue Triage

### Issue Labels

| Label | Description |
|-------|-------------|
| `bug` | Something isn't working |
| `enhancement` | New feature or request |
| `documentation` | Improvements or additions to documentation |
| `good first issue` | Good for newcomers |
| `help wanted` | Extra attention is needed |
| `priority: high` | High priority issue |
| `priority: low` | Low priority issue |
| `status: needs-review` | Needs review from maintainers |
| `status: blocked` | Blocked by other issues |

### Component Labels

- `component: frontend` - Frontend-related issues
- `component: backend` - Backend-related issues
- `component: docs` - Documentation-related
- `component: ci/cd` - CI/CD and deployment
- `component: testing` - Testing framework and tests

## 🌍 Community & Support

### Communication Channels

- **💬 Discord**: [Join our community](https://discord.gg/your-invite) - For real-time chat
- **🐛 GitHub Issues**: For bug reports and feature requests
- **💭 GitHub Discussions**: For questions and general discussion
- **📧 Email**: [maintainers@ollamastack.com](mailto:maintainers@ollamastack.com) - For private matters

### Getting Help

- **New to the project?** Check our [Getting Started guide](../README.md#quick-start)
- **Technical questions?** Use GitHub Discussions
- **Found a bug?** Create a GitHub Issue
- **Need real-time help?** Join our Discord

### Recognition

We appreciate all contributions! Contributors will be:

- **Listed in our README** - All contributors are acknowledged
- **Featured in releases** - Major contributions highlighted
- **Invited to maintainer team** - For ongoing contributors
- **Given special Discord roles** - Based on contribution level

## 📋 Development Resources

### Useful Commands

```bash
# Development
npm run dev                    # Start all dev servers
npm run dev:frontend          # Start frontend only
npm run dev:backend           # Start backend only

# Testing
npm test                      # Run all tests
npm run test:watch           # Run tests in watch mode
npm run test:coverage        # Run with coverage report

# Code Quality
npm run lint                 # Lint all code
npm run lint:fix            # Fix linting issues
npm run format              # Format all code
npm run type-check          # TypeScript type checking

# Building
npm run build               # Build for production
npm run build:frontend      # Build frontend
npm run build:backend       # Build backend Docker image

# Database
npm run db:migrate          # Run database migrations
npm run db:seed             # Seed database with test data

# Documentation
npm run docs:dev            # Start documentation server
npm run docs:build          # Build documentation
```

### IDE Setup

#### VS Code Extensions

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.black-formatter",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-typescript-next",
    "ms-vscode.vscode-eslint",
    "ms-vscode-remote.remote-containers"
  ]
}
```

#### Settings

```json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "python.formatting.provider": "black",
  "typescript.preferences.importModuleSpecifier": "relative"
}
```

### Learning Resources

- **Next.js**: [Official Documentation](https://nextjs.org/docs)
- **FastAPI**: [Official Documentation](https://fastapi.tiangolo.com/)
- **LangChain**: [Official Documentation](https://docs.langchain.com/)
- **Tailwind CSS**: [Official Documentation](https://tailwindcss.com/docs)
- **TypeScript**: [Official Handbook](https://www.typescriptlang.org/docs/)

## 🎉 Thank You!

Thank you for taking the time to contribute to OllamaStack! Every contribution, no matter how small, helps make this project better for everyone.

**Happy coding!** 🚀

---

*For questions about this contributing guide, please reach out in our [Discord community](https://discord.gg/your-invite) or create an issue.* 