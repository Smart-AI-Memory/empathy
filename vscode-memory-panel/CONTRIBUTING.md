# Contributing to Empathy Memory Panel

Thank you for your interest in contributing to the Empathy Memory Panel extension!

## Development Setup

### Prerequisites
- Node.js 18+ and npm
- VS Code 1.85.0+
- Python 3.10+
- Git

### Initial Setup

```bash
# Clone repository
git clone https://github.com/your-org/empathy-framework.git
cd empathy-framework/vscode-memory-panel

# Install dependencies
npm install

# Compile TypeScript
npm run compile
```

### Running in Development

1. Open the extension directory in VS Code
2. Press `F5` to launch Extension Development Host
3. Test changes in the new VS Code window
4. Make changes to source files
5. Reload Extension Development Host (`Ctrl+R`) to see changes

### Watch Mode

For active development:
```bash
npm run watch
```

This will automatically recompile TypeScript on file changes.

## Project Structure

```
vscode-memory-panel/
├── src/
│   ├── extension.ts              # Extension entry point
│   ├── services/
│   │   └── MemoryAPIService.ts   # HTTP client
│   └── views/
│       └── MemoryPanelProvider.ts # Webview provider
├── webview/
│   ├── index.html                # Panel UI
│   └── styles.css                # Styling
├── media/                        # Icons and images
├── package.json                  # Extension manifest
├── tsconfig.json                 # TypeScript config
└── README.md                     # Documentation
```

## Code Style

### TypeScript
- Use TypeScript strict mode
- Define interfaces for all API responses
- Add JSDoc comments for public APIs
- Follow VS Code extension best practices

Example:
```typescript
/**
 * Get memory system status
 * @returns Promise resolving to memory status
 */
async getStatus(): Promise<MemoryStatus> {
    return this.request<MemoryStatus>('GET', '/api/status');
}
```

### HTML/CSS
- Use semantic HTML
- Follow VS Code webview guidelines
- Use CSS variables for theming
- Ensure accessibility (ARIA labels, keyboard navigation)

### Python
- Follow PEP 8
- Add type hints
- Use async/await for I/O operations
- Include docstrings

## Testing

### Manual Testing
1. Start the API server: `python api_server_example.py`
2. Launch Extension Development Host (F5)
3. Test all features:
   - Status display
   - Redis start/stop
   - Pattern listing
   - Health check
   - Export functionality

### Automated Testing
```bash
npm test
```

## Adding Features

### 1. New API Endpoint

**Backend (Python):**
```python
@app.get("/api/new-feature")
async def new_feature():
    # Implementation
    return {"data": "value"}
```

**Frontend (TypeScript):**
```typescript
// In MemoryAPIService.ts
async getNewFeature(): Promise<NewFeatureResponse> {
    return this.request<NewFeatureResponse>('GET', '/api/new-feature');
}
```

**UI (HTML):**
```html
<!-- In index.html -->
<button id="new-feature-btn" class="btn btn-primary">
    New Feature
</button>
```

**Event Handler (JavaScript in HTML):**
```javascript
elements.newFeatureBtn.addEventListener('click', () => {
    vscode.postMessage({ type: 'newFeature' });
});
```

**Provider (TypeScript):**
```typescript
// In MemoryPanelProvider.ts
case 'newFeature':
    await this._handleNewFeature();
    break;
```

### 2. New UI Section

1. Add HTML in `webview/index.html`
2. Add styles in `webview/styles.css`
3. Add message handler in MemoryPanelProvider
4. Update API service if needed

## Pull Request Process

1. **Fork** the repository
2. **Create branch**: `git checkout -b feature/my-feature`
3. **Make changes** with clear commits
4. **Test thoroughly**
5. **Run linter**: `npm run lint`
6. **Update docs** if needed
7. **Submit PR** with description

### PR Checklist
- [ ] Code compiles without errors
- [ ] Linter passes (`npm run lint`)
- [ ] Manually tested all changes
- [ ] Updated README.md if needed
- [ ] Added comments for complex logic
- [ ] Follows existing code style

## Commit Messages

Use conventional commits:
```
feat: Add pattern search functionality
fix: Resolve Redis connection timeout
docs: Update API endpoint documentation
refactor: Simplify status update logic
test: Add health check tests
```

## Bug Reports

When reporting bugs, include:
- VS Code version
- Extension version
- Steps to reproduce
- Expected vs actual behavior
- Error messages/screenshots
- Backend logs if applicable

## Feature Requests

For new features, describe:
- Use case
- Proposed solution
- Alternative approaches considered
- UI mockups if applicable

## Security

For security issues:
- Do NOT open public issues
- Email: security@empathyframework.com
- Include detailed description
- Allow time for fix before disclosure

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism
- Focus on what's best for the project
- Show empathy (fitting for this project!)

## License

By contributing, you agree that your contributions will be licensed under the Fair Source License 0.9.

## Questions?

- Documentation: [README.md](./README.md)
- Quickstart: [QUICKSTART.md](./QUICKSTART.md)
- Issues: GitHub Issues
- Email: dev@empathyframework.com

## Recognition

Contributors will be recognized in:
- CHANGELOG.md
- README.md (Contributors section)
- Git commit history

Thank you for contributing to Empathy Framework!
