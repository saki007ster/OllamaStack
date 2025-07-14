# Contributing to OllamaStack

Thank you for your interest in contributing to OllamaStack! We welcome contributions from everyone and are grateful for your help in making this project better.

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:
- **Node.js** 20+ and **npm**
- **Python** 3.11+
- **Docker** and **Docker Compose**
- **Git**

### Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/saki007ster/ollamastack.git
   cd ollamastack
   ```
3. **Install dependencies**:
   ```bash
   npm run install:all
   ```
4. **Set up environment**:
   ```bash
   cp backend/env.example backend/.env
   ```
5. **Start the development environment**:
   ```bash
   docker-compose up --build
   ```

## 🛠️ Development Workflow

### Making Changes

1. **Create a new branch** for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our coding standards

3. **Test your changes**:
   ```bash
   npm test
   ```

4. **Lint and format your code**:
   ```bash
   npm run lint
   npm run format
   ```

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add amazing new feature"
   ```

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request** on GitHub

## 📋 Code Standards

### Python (Backend)

- Follow **PEP 8** style guidelines
- Use **type hints** for all function parameters and return values
- Write **docstrings** for all public functions and classes
- Use **async/await** for I/O operations
- Keep functions focused and small (< 50 lines when possible)

Example:
```python
async def create_chat_response(
    message: str, 
    conversation_id: str,
    temperature: float = 0.7
) -> ChatResponse:
    """Create a chat response using the LLM.
    
    Args:
        message: The user's input message
        conversation_id: Unique conversation identifier
        temperature: Response randomness (0.0-1.0)
        
    Returns:
        ChatResponse object with the LLM's reply
    """
    # Implementation here
```

### TypeScript (Frontend)

- Use **TypeScript** for all new code
- Follow **React best practices** and hooks patterns
- Use **functional components** with hooks
- Implement proper **error boundaries**
- Use **Tailwind CSS** for styling

Example:
```typescript
interface ChatInputProps {
  onSendMessage: (message: string) => Promise<void>;
  disabled?: boolean;
  placeholder?: string;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  disabled = false,
  placeholder = "Type your message..."
}) => {
  // Implementation here
};
```

### Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or modifying tests
- `chore:` - Maintenance tasks

Examples:
- `feat: add conversation history endpoint`
- `fix: resolve memory leak in agent service`
- `docs: update README installation steps`

## 🧪 Testing

### Backend Testing

```bash
# Run all backend tests
npm run test:backend

# Run with coverage
cd backend && python -m pytest --cov=app

# Run specific test file
cd backend && python -m pytest tests/test_main.py
```

### Frontend Testing

```bash
# Run all frontend tests
npm run test:frontend

# Run in watch mode
cd frontend && npm run test:watch

# Run with coverage
cd frontend && npm test -- --coverage
```

### Writing Tests

- Write tests for all new features
- Maintain test coverage above 80%
- Use descriptive test names
- Test both success and error cases

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Environment details** (OS, Python/Node versions, Docker version)
2. **Steps to reproduce** the issue
3. **Expected vs actual behavior**
4. **Error messages** or logs
5. **Screenshots** if applicable

Use our bug report template:

```markdown
**Environment:**
- OS: [e.g., macOS 14.0]
- Python: [e.g., 3.11.5]
- Node.js: [e.g., 20.8.0]
- Docker: [e.g., 24.0.6]

**Steps to Reproduce:**
1. Start the application with `docker-compose up`
2. Navigate to chat interface
3. Send message "Hello"
4. Observe error

**Expected Behavior:**
The message should be sent to the LLM and a response should appear.

**Actual Behavior:**
Error message appears: "Connection failed"

**Additional Context:**
[Any additional information, logs, or screenshots]
```

## ✨ Feature Requests

We love new ideas! When suggesting features:

1. **Check existing issues** to avoid duplicates
2. **Describe the problem** you're trying to solve
3. **Propose a solution** with examples
4. **Consider implementation** complexity and scope
5. **Think about backwards compatibility**

## 📦 Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new functionality
3. **Ensure all tests pass**
4. **Update the changelog** if applicable
5. **Request review** from maintainers

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

## 🏗️ Architecture Guidelines

### Backend Architecture

- Use **dependency injection** patterns
- Implement **proper error handling** with custom exceptions
- Follow **RESTful API** conventions
- Use **Pydantic models** for data validation
- Implement **logging** throughout the application

### Frontend Architecture

- Use **component composition** over inheritance
- Implement **proper state management** (React hooks)
- Follow **accessibility** best practices
- Use **TypeScript** for type safety
- Implement **error boundaries**

## 🎯 Focus Areas

We're particularly interested in contributions in these areas:

- **New LangChain tools and agents**
- **UI/UX improvements**
- **Performance optimizations**
- **Security enhancements**
- **Documentation improvements**
- **Test coverage**
- **Deployment options**

## 💬 Getting Help

- **Discord**: [Join our community](https://discord.gg/ollamastack)
- **GitHub Discussions**: For feature discussions and questions
- **GitHub Issues**: For bug reports and specific problems

## 📜 Code of Conduct

We are committed to providing a welcoming and inspiring community for all. Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before participating.

## 🙏 Recognition

All contributors will be recognized in our README and release notes. Thank you for making OllamaStack better for everyone!

---

**Happy Contributing! 🚀** 