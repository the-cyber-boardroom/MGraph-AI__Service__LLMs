# LLM Collaboration Templates

## Initial Component Creation

### Template: Create First Component
```markdown
I need to create a web component for [purpose].

## Technical Requirements
- Use ES6 class extending HTMLElement
- No external JavaScript dependencies
- Self-contained with its own CSS
- Must work with these API endpoints:
  - POST /api/[endpoint1] - [description]
  - GET /api/[endpoint2] - [description]

## Component Specifications
Name: [ComponentName]
Element tag: <component-name>

## Functionality
1. [Core feature 1 with details]
2. [Core feature 2 with details]
3. [Core feature 3 with details]

## UI Requirements
- [Layout description]
- [Interactive elements]
- [Visual feedback states]

## Event Communication
This component should:
- Listen for: [event-name] events from [source]
- Emit: [event-name] events when [condition]

## Code Structure
Please create:
1. component-name.js with the component class
2. component-name.css with styles
3. Usage example for index.html

Include:
- Constructor with state initialization
- connectedCallback with render and event setup
- disconnectedCallback for cleanup
- Error handling for API calls
- Loading states during async operations
```

### Template: Core Application Structure
```markdown
I need the main application structure for a [type] application.

## Application Overview
[Brief description of what the app does]

## File Structure Needed
project/
├── index.html
├── css/
│   ├── main.css (global styles and variables)
│   └── components.css
├── js/
│   ├── app.js (main application)
│   ├── components/
│   └── utils/
│       └── api-client.js

## Global CSS Variables
- Primary color: #667eea
- Background: #ffffff
- Text: #212529
- Border: #dee2e6

## API Client Requirements
Base URL: /api
Methods needed:
- GET, POST, PUT, DELETE
- Error handling
- Response parsing
- Optional caching

## HTML Structure
Create index.html with:
- Proper meta tags
- Component mounting points
- CSS imports
- ES6 module scripts

Please generate all files with complete implementations.
```

## Feature Addition

### Template: Add Feature to Existing Component
```markdown
I need to add [feature] to an existing component.

## Current Component
```javascript
[Paste current component code]
```

## New Feature Requirements
Feature: [Name and description]

Functionality:
1. [Specific requirement 1]
2. [Specific requirement 2]

UI Changes:
- [New elements to add]
- [Existing elements to modify]

## API Integration
New endpoint to use:
- [Method] /api/[endpoint]
- Request: { [schema] }
- Response: { [schema] }

## Event Updates
New events to handle:
- [event-name]: [when triggered]
New events to emit:
- [event-name]: [when to emit]

## Constraints
- Maintain backward compatibility
- Preserve existing functionality
- Follow current code patterns
- Keep component self-contained

Please provide:
1. Updated component code
2. Any CSS additions needed
3. Integration instructions
```

### Template: Add Interactivity
```markdown
Add [interaction type] to the component.

## Current State
[Describe what currently exists]

## Desired Interaction
When user [action], the component should [response].

## Specific Requirements
- Trigger: [mouse/keyboard/touch event]
- Visual feedback: [what user sees]
- State change: [what changes in component]
- API call: [if needed]
- Success behavior: [what happens on success]
- Error behavior: [what happens on failure]

## Example Flow
1. User clicks [element]
2. Show [loading state]
3. Call [API endpoint]
4. Update [UI element]
5. Emit [event] for other components

Please implement with proper event handlers and state management.
```

## Bug Fix Pattern

### Template: Debug API Integration
```markdown
Component API call is failing.

## Current Code
```javascript
[Paste relevant code section]
```

## Error Details
- Error message: [exact error]
- When it occurs: [user action that triggers it]
- Expected behavior: [what should happen]
- Actual behavior: [what's happening]

## API Endpoint Details
- URL: [full endpoint]
- Method: [GET/POST/etc]
- Headers required: [any headers]
- Request format: [example request]
- Response format: [example response]

## Environment
- Browser: [Chrome/Firefox/Safari]
- Console errors: [paste any]
- Network tab shows: [request/response details]

Please provide:
1. Fixed code with proper error handling
2. Console.log statements for debugging
3. Explanation of the issue
```

### Template: Fix UI Rendering Issue
```markdown
UI element not rendering correctly.

## Issue Description
[Element] is [problem description].

## Current Rendering Code
```javascript
render() {
    [Paste render method]
}
```

## Current CSS
```css
[Paste relevant CSS]
```

## Expected Appearance
[Description or sketch of desired look]

## Actual Appearance  
[Description of current problem]

## Browser Specifics
- Works in: [browsers where it works]
- Broken in: [browsers where it's broken]
- Responsive breakpoint: [if relevant]

Fix requirements:
- Maintain current functionality
- Cross-browser compatible
- Responsive if applicable
- Follow existing CSS patterns
```

## Consolidation

### Template: Consolidate Versions to Production
```markdown
Consolidate versions v0.1 through v0.5 into production v1.0.

## Features to Consolidate

### From v0.1
- [Feature list]
- Component: [component-name.js]

### From v0.2  
- [Feature list]
- Enhancements: [list]

### From v0.3
- [Feature list]
- New components: [list]

### From v0.4
- [Feature list]
- New components: [list]

### From v0.5
- [Feature list]
- New components: [list]

## Target Structure
v1.0/
├── index.html
├── css/
│   ├── main.css
│   └── [component styles]
├── components/
│   ├── [component folders]
├── services/
│   └── api-client.js
└── utils/
    └── [utilities]

## Consolidation Rules
1. Take best implementation of each feature
2. Merge duplicate utilities
3. Consistent naming throughout
4. Single source of truth for each component
5. Unified event system

## Quality Requirements
- No console.errors
- All API endpoints working
- Loading states for async operations
- Error handling throughout
- Memory leak prevention

Please create the complete v1.0 structure with all files.
```

### Template: Component Merger
```markdown
Merge multiple versions of [ComponentName] into single best version.

## Version Implementations

### v0.2 Implementation
```javascript
[Paste v0.2 code]
```
Features: [list unique features]

### v0.3 Implementation  
```javascript
[Paste v0.3 code]
```
Features: [list unique features]

### v0.5 Implementation
```javascript
[Paste v0.5 code]
```
Features: [list unique features]

## Merge Requirements
- Include all unique features
- Use best code patterns from any version
- Maintain all event communications
- Preserve all API integrations
- Optimize for performance
- Clean up redundant code

## Test Cases
After merge, component should:
1. [Test case 1]
2. [Test case 2]
3. [Test case 3]

Generate merged component with all features integrated.
```

## API Integration

### Template: Connect Component to FastAPI
```markdown
Connect component to FastAPI backend.

## Component Functionality
[Describe what component does]

## FastAPI Endpoint
```python
@app.post("/api/[endpoint]")
async def endpoint_name(request: RequestModel):
    # Implementation
    return ResponseModel
```

## Request/Response Models
Request:
```json
{
  "field1": "type",
  "field2": "type"
}
```

Response:
```json
{
  "status": "success",
  "data": {},
  "cache_id": "string"
}
```

## Component Integration Needs
1. Call API when [trigger]
2. Show loading during request
3. Handle success response
4. Handle error response
5. Update UI with data
6. Cache if appropriate

## Error Cases to Handle
- Network failure
- 400 Bad Request
- 401 Unauthorized  
- 404 Not Found
- 500 Server Error
- Timeout

Please implement complete API integration with all error handling.
```

### Template: Add Caching Layer
```markdown
Add caching to API calls in component.

## Current API Calls
```javascript
[Paste current API methods]
```

## Caching Requirements
- Cache duration: [time in ms]
- Cache key: [how to generate]
- Cache invalidation: [when to clear]
- Storage: Memory (Map) / localStorage
- Size limit: [max entries]

## Cache Strategy
- Cache hit: Return immediately
- Cache miss: Fetch and store
- Cache stale: Background refresh
- Cache full: LRU eviction

## Implementation Needs
1. Cache wrapper for API calls
2. Cache timestamp tracking
3. Cache size management
4. Cache clear methods
5. Debug logging for cache hits/misses

Generate caching implementation following this strategy.
```

## Advanced Patterns

### Template: Add Real-time Updates
```markdown
Add real-time update capability to component.

## Update Mechanism
- Method: [WebSocket/SSE/Polling]
- Endpoint: [URL]
- Frequency: [if polling]

## Events to Handle
- Connection established
- Message received
- Connection lost  
- Reconnection
- Error

## Update Flow
1. Establish connection on component mount
2. Listen for updates
3. Process update data
4. Update UI smoothly
5. Handle disconnections gracefully

## State Synchronization
- Initial state: [how to load]
- Update merging: [how to merge updates]
- Conflict resolution: [if needed]

Implement real-time updates with proper lifecycle management.
```

### Template: Add Complex State Management
```markdown
Add state management to coordinate multiple components.

## State Structure
```javascript
{
  global: {
    user: {},
    settings: {}
  },
  local: {
    component1: {},
    component2: {}
  }
}
```

## State Operations Needed
- Initialize state
- Update state section
- Subscribe to changes
- Broadcast updates
- Persist to storage
- Restore from storage

## Component Integration
Components that need state:
- Component1: needs [state sections]
- Component2: needs [state sections]

## State Flow
1. Component dispatches action
2. State manager processes
3. State updated
4. Subscribers notified
5. Components re-render

Implement state management without external libraries.
```

## Performance Optimization

### Template: Optimize Component Performance
```markdown
Optimize [ComponentName] for better performance.

## Current Performance Issues
- [Issue 1: description and measurement]
- [Issue 2: description and measurement]

## Current Code
```javascript
[Paste relevant code]
```

## Optimization Targets
- Initial render: < [X]ms
- Re-render: < [X]ms  
- Memory usage: < [X]MB
- API calls: minimize

## Optimization Strategies
1. [Strategy 1: e.g., debouncing]
2. [Strategy 2: e.g., virtual scrolling]
3. [Strategy 3: e.g., lazy loading]

## Constraints
- Maintain all functionality
- Keep code readable
- No external dependencies
- Browser compatibility

Implement optimizations with measurements.
```