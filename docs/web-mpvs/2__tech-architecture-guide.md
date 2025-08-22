# Technical Architecture Guide

## Web Components Pattern (HTMLElement)

### Core Component Structure
```javascript
export class ComponentName extends HTMLElement {
    constructor() {
        super();
        // Initialize internal state
        this.state = {};
        this.listeners = [];
    }
    
    connectedCallback() {
        // Called when element is added to DOM
        this.render();
        this.setupEventListeners();
        this.initialize();
    }
    
    disconnectedCallback() {
        // Cleanup when removed from DOM
        this.cleanup();
    }
    
    render() {
        // Generate and inject HTML
        this.className = 'component-name';
        this.innerHTML = `<!-- HTML structure -->`;
        
        // Cache DOM references
        this.cacheElements();
    }
    
    cacheElements() {
        // Store references to frequently accessed elements
        this.button = this.querySelector('#button');
        this.input = this.querySelector('#input');
    }
    
    setupEventListeners() {
        // Attach event handlers
    }
    
    cleanup() {
        // Remove event listeners
        // Clear timers
        // Release resources
    }
}
```

### Component Registration
```javascript
// Register once, use everywhere
customElements.define('component-name', ComponentName);
```

### Component Communication Patterns
```javascript
// Emitting custom events
this.dispatchEvent(new CustomEvent('component-action', {
    detail: { data: 'value' },
    bubbles: true
}));

// Listening to events
this.addEventListener('other-component-event', (e) => {
    this.handleEvent(e.detail);
});
```

## Zero-Dependency Philosophy

### Why Zero Dependencies?
1. **Longevity**: No framework churn or version conflicts
2. **Performance**: No bundle overhead or loading delays
3. **Simplicity**: Direct browser APIs, no abstraction layers
4. **Debugging**: Stack traces point to your code
5. **Learning**: Understand the web platform itself

### Native API Usage
```javascript
// Instead of jQuery
this.querySelector('.element');
this.querySelectorAll('.elements');

// Instead of Lodash
Array.from(items).map(item => transform(item));
[...new Set(array)]; // Unique values

// Instead of Axios
fetch('/api/endpoint', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
});

// Instead of Moment.js
new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
}).format(date);
```

## FastAPI Backend Integration

### API Client Pattern
```javascript
export class APIClient {
    constructor(baseURL = '/api') {
        this.baseURL = baseURL;
    }
    
    async request(endpoint, options = {}) {
        const response = await fetch(`${this.baseURL}${endpoint}`, {
            headers: { 'Content-Type': 'application/json' },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }
        
        return await response.json();
    }
    
    async get(endpoint) {
        return this.request(endpoint);
    }
    
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
}
```

### Backend Endpoints Structure
```python
# FastAPI backend structure
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# API routes
@app.post("/api/analyze")
async def analyze(data: dict):
    return {"result": process(data)}

# Serve static files
app.mount("/", StaticFiles(directory="static", html=True))
```

### CORS-Free Development
```nginx
# Nginx configuration for same-origin serving
location / {
    root /var/www/html;
    try_files $uri $uri/ /index.html;
}

location /api {
    proxy_pass http://localhost:8000;
    proxy_set_header Host $host;
}
```

## Event-Driven Communication

### Event Flow Architecture
```
User Action → Component Event → Parent Handler → State Update → Child Updates
```

### Event Types
```javascript
// 1. User-initiated events
this.button.addEventListener('click', (e) => {
    this.handleClick(e);
});

// 2. Component lifecycle events
this.dispatchEvent(new CustomEvent('component-ready', {
    detail: { id: this.id }
}));

// 3. Data change events
this.dispatchEvent(new CustomEvent('data-updated', {
    detail: { oldValue, newValue }
}));

// 4. Error events
this.dispatchEvent(new CustomEvent('component-error', {
    detail: { error: error.message }
}));
```

### Event Namespacing
```javascript
// Consistent naming convention
'component-name:action'
'analysis-panel:tab-changed'
'chat-panel:message-sent'
'api-client:request-complete'
```

## State Management Patterns

### Component-Local State
```javascript
class StatefulComponent extends HTMLElement {
    constructor() {
        super();
        this.state = {
            items: [],
            selectedId: null,
            loading: false
        };
    }
    
    setState(updates) {
        const oldState = { ...this.state };
        this.state = { ...this.state, ...updates };
        this.onStateChange(oldState, this.state);
    }
    
    onStateChange(oldState, newState) {
        // React to specific changes
        if (oldState.loading !== newState.loading) {
            this.updateLoadingUI(newState.loading);
        }
    }
}
```

### Global State via Events
```javascript
// State coordinator pattern
class StateCoordinator extends HTMLElement {
    constructor() {
        super();
        this.globalState = {};
    }
    
    connectedCallback() {
        // Listen for state change requests
        window.addEventListener('state:update', (e) => {
            this.updateGlobalState(e.detail);
        });
    }
    
    updateGlobalState(changes) {
        this.globalState = { ...this.globalState, ...changes };
        
        // Broadcast state change
        window.dispatchEvent(new CustomEvent('state:changed', {
            detail: this.globalState
        }));
    }
}
```

### Cache-Aware State
```javascript
class CacheAwareComponent extends HTMLElement {
    constructor() {
        super();
        this.cache = new Map();
    }
    
    async fetchData(key) {
        // Check cache first
        if (this.cache.has(key)) {
            const cached = this.cache.get(key);
            if (Date.now() - cached.timestamp < 300000) { // 5 min
                return cached.data;
            }
        }
        
        // Fetch fresh data
        const data = await this.apiClient.get(`/data/${key}`);
        
        // Update cache
        this.cache.set(key, {
            data,
            timestamp: Date.now()
        });
        
        return data;
    }
}
```

## File Organization

### Version Structure
```
version/
├── index.html
├── css/
│   ├── main.css
│   ├── variables.css
│   └── components/
│       ├── component1.css
│       └── component2.css
├── components/
│   ├── component1/
│   │   ├── component1.js
│   │   └── component1.css
│   └── component2/
│       ├── component2.js
│       └── component2.css
├── services/
│   └── api-client.js
└── utils/
    ├── formatter.js
    └── validators.js
```

### Import Strategy
```javascript
// ES6 modules with relative paths
import { APIClient } from '../services/api-client.js';
import { formatDate } from '../utils/formatter.js';

// CSS imports in HTML
<link rel="stylesheet" href="./css/main.css">
<link rel="stylesheet" href="./components/panel/panel.css">
```

## Performance Patterns

### Lazy Component Loading
```javascript
// Register component only when needed
if (document.querySelector('complex-component')) {
    import('./components/complex-component.js').then(module => {
        customElements.define('complex-component', module.ComplexComponent);
    });
}
```

### Debounced Actions
```javascript
class SearchComponent extends HTMLElement {
    constructor() {
        super();
        this.searchTimeout = null;
    }
    
    handleInput(e) {
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(() => {
            this.performSearch(e.target.value);
        }, 300);
    }
}
```

### Virtual Scrolling
```javascript
class LargeList extends HTMLElement {
    renderVisibleItems() {
        const scrollTop = this.scrollContainer.scrollTop;
        const startIndex = Math.floor(scrollTop / this.itemHeight);
        const endIndex = startIndex + this.visibleCount;
        
        this.renderItems(startIndex, endIndex);
    }
}
```