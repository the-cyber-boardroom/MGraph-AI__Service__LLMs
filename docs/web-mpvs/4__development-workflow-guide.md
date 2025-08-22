# Development Workflow Guide

## Initial Brief Creation

### Pre-Development Checklist
```markdown
Project Setup:
- [ ] Clear problem definition
- [ ] Target users identified
- [ ] Core features listed (max 3-5 for v0.1)
- [ ] FastAPI backend operational
- [ ] API endpoints documented
- [ ] Development environment ready
```

### Effective LLM Brief Structure
```markdown
## Context
I'm building a [type] application that [purpose].

## Technical Constraints
- Pure JavaScript (ES6+), no external dependencies
- HTMLElement web components
- FastAPI backend at [endpoints]
- Must be self-contained in version folder

## Core Functionality Needed
1. [Feature 1 with clear description]
2. [Feature 2 with clear description]
3. [Feature 3 with clear description]

## Current Structure
[Paste file tree if continuing from previous version]

## Specific Task
Create [specific component/feature] that:
- [Requirement 1]
- [Requirement 2]
- [Requirement 3]

## Success Criteria
- Works with real API (no mocks)
- Follows existing patterns (if any)
- Self-contained component
- Includes error handling
```

## UX-First Development

### The UX Flow Process

#### 1. Sketch the Experience
```
Before coding:
1. Draw/describe user journey
2. Identify key interactions
3. Define success states
4. Plan error states
5. Consider edge cases
```

#### 2. Describe to LLM
```markdown
"I need a chat interface where:
- Users type text in a resizable textarea
- Character count shows with color warnings
- Enter sends, Shift+Enter adds newline
- Messages appear in bubbles with timestamps
- Auto-scroll to latest message
- Sample text button for quick testing"
```

#### 3. Iterate on Generated UI
```javascript
// LLM generates initial implementation
// You test and refine:

// Original from LLM
handleSend() {
    const text = this.input.value;
    this.sendMessage(text);
}

// Your UX refinement
handleSend() {
    const text = this.input.value.trim();
    if (!text) return;  // Prevent empty messages
    
    this.setLoading(true);
    this.sendMessage(text);
    this.input.value = '';  // Clear immediately for responsiveness
    this.input.focus();     // Keep focus for multiple messages
}
```

### UX Testing Patterns

#### Immediate Feedback Testing
```javascript
// Add console logs during development
handleUserAction(e) {
    console.log('Action triggered:', e.type, e.target);
    // Immediate visual feedback
    e.target.classList.add('active');
    
    // Process action
    this.processAction(e.detail);
    
    // Remove feedback
    setTimeout(() => e.target.classList.remove('active'), 200);
}
```

#### Progressive Enhancement
```
v0.1: Basic functionality works
v0.2: Add loading states and transitions
v0.3: Add keyboard shortcuts
v0.4: Add drag-and-drop support
v0.5: Add accessibility features
```

## Real-Time API Integration

### Backend First Approach

#### 1. Create FastAPI Endpoints
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class AnalysisRequest(BaseModel):
    text: str
    options: dict = {}

@app.post("/api/analyze")
async def analyze(request: AnalysisRequest):
    try:
        result = process_text(request.text)
        return {
            "status": "success",
            "data": result,
            "cache_id": generate_cache_id()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### 2. Test Endpoints Directly
```bash
# Test with curl before UI implementation
curl -X POST "http://localhost:8000/api/analyze" \
     -H "Content-Type: application/json" \
     -d '{"text": "test content"}'
```

#### 3. Integrate in Component
```javascript
class AnalysisComponent extends HTMLElement {
    async analyzeText(text) {
        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });
            
            if (!response.ok) {
                throw new Error(`API Error: ${response.status}`);
            }
            
            const data = await response.json();
            this.handleSuccess(data);
            
        } catch (error) {
            this.handleError(error);
        }
    }
    
    handleSuccess(data) {
        console.log('API Response:', data);
        this.updateUI(data);
    }
    
    handleError(error) {
        console.error('API Error:', error);
        this.showError('Failed to analyze text. Please try again.');
    }
}
```

### API Integration Patterns

#### Parallel Requests
```javascript
async fetchAllData() {
    // Show loading for all sections
    this.setLoading(true);
    
    try {
        // Parallel execution for speed
        const [facts, questions, hypotheses] = await Promise.all([
            this.api.getFacts(this.text),
            this.api.getQuestions(this.text),
            this.api.getHypotheses(this.text)
        ]);
        
        // Update UI with all results
        this.updateResults({ facts, questions, hypotheses });
        
    } catch (error) {
        // Handle partial failures
        console.error('Some requests failed:', error);
    } finally {
        this.setLoading(false);
    }
}
```

#### Retry Logic
```javascript
async fetchWithRetry(url, options, maxRetries = 3) {
    for (let i = 0; i < maxRetries; i++) {
        try {
            const response = await fetch(url, options);
            if (response.ok) return response.json();
            
            if (response.status === 429) {
                // Rate limited - wait before retry
                await new Promise(r => setTimeout(r, 1000 * (i + 1)));
                continue;
            }
            
            throw new Error(`HTTP ${response.status}`);
        } catch (error) {
            if (i === maxRetries - 1) throw error;
            await new Promise(r => setTimeout(r, 500));
        }
    }
}
```

## Testing Without Mocks

### Real Data Testing Strategy

#### 1. Seed Data Preparation
```python
# FastAPI endpoint for consistent test data
@app.get("/api/test-data")
async def get_test_data():
    return {
        "samples": [
            "Technical analysis text...",
            "Business report text...",
            "Research paper text..."
        ]
    }
```

#### 2. Component Testing
```javascript
class TestableComponent extends HTMLElement {
    async runTests() {
        const testCases = await this.loadTestData();
        
        for (const testCase of testCases) {
            console.log(`Testing: ${testCase.name}`);
            
            const result = await this.processData(testCase.input);
            
            // Verify expectations
            console.assert(result.facts.length > 0, 'Should extract facts');
            console.assert(result.questions.length > 0, 'Should generate questions');
        }
    }
}
```

#### 3. Error Condition Testing
```javascript
// Test error handling with real API
async testErrorHandling() {
    // Test with invalid data
    await this.api.analyze('');  // Empty text
    await this.api.analyze('x'.repeat(10000));  // Too long
    await this.api.analyze(null);  // Null input
    
    // Verify graceful degradation
    console.assert(this.hasErrorUI, 'Should show error UI');
}
```

## Refactoring Patterns

### Progressive Refactoring

#### Stage 1: Make it Work
```javascript
// Initial implementation - focus on functionality
handleClick() {
    const text = document.getElementById('input').value;
    fetch('/api/analyze', {
        method: 'POST',
        body: JSON.stringify({ text })
    }).then(r => r.json()).then(data => {
        document.getElementById('output').innerHTML = data.result;
    });
}
```

#### Stage 2: Make it Right
```javascript
// Refactored for maintainability
async handleClick() {
    const text = this.getInputText();
    
    if (!this.validateInput(text)) {
        return this.showValidationError();
    }
    
    try {
        const result = await this.analyzeText(text);
        this.displayResult(result);
    } catch (error) {
        this.handleError(error);
    }
}
```

#### Stage 3: Make it Fast
```javascript
// Optimized version
async handleClick() {
    const text = this.getInputText();
    
    // Check cache first
    const cached = this.cache.get(text);
    if (cached && !this.isStale(cached)) {
        return this.displayResult(cached.data);
    }
    
    // Debounce rapid clicks
    if (this.pending) return;
    this.pending = true;
    
    try {
        const result = await this.analyzeText(text);
        this.cache.set(text, { data: result, time: Date.now() });
        this.displayResult(result);
    } finally {
        this.pending = false;
    }
}
```

### Component Extraction

#### Identify Reusable Parts
```javascript
// Before: Monolithic component
class BigComponent extends HTMLElement {
    render() {
        this.innerHTML = `
            <div class="header">...</div>
            <div class="chat">...</div>
            <div class="analysis">...</div>
        `;
    }
}

// After: Composed components
class AppComponent extends HTMLElement {
    render() {
        this.innerHTML = `
            <app-header></app-header>
            <chat-panel></chat-panel>
            <analysis-panel></analysis-panel>
        `;
    }
}
```

### Event System Refactoring

#### From Tight Coupling to Events
```javascript
// Before: Direct method calls
class ComponentA {
    processData(data) {
        const result = this.analyze(data);
        componentB.updateDisplay(result);  // Tight coupling
    }
}

// After: Event-driven
class ComponentA {
    processData(data) {
        const result = this.analyze(data);
        this.dispatchEvent(new CustomEvent('data-processed', {
            detail: result,
            bubbles: true
        }));
    }
}
```

## Workflow Optimization Tips

### Batch Processing
- Group related changes together
- Generate multiple components in one LLM session
- Test all changes before next iteration

### Context Management
```markdown
## Session Context for LLM
Current version: v0.3
Previous features: [list what's working]
Current task: [specific addition]
Constraints: [any specific requirements]
```

### Rapid Iteration Loop
```
1. Describe feature (2 min)
2. Generate code (LLM)
3. Integrate (5 min)
4. Test with API (2 min)
5. Refine if needed (5 min)
Total: ~15 minutes per feature
```

### Common Time Sinks to Avoid
- Perfecting CSS before functionality works
- Over-engineering state management
- Creating abstractions too early
- Debugging without console.log
- Not testing with real data immediately

### Productivity Metrics
Track your flow state efficiency:
- Features completed per hour
- Lines of working code per session
- Time from idea to working feature
- Number of iteration cycles needed
- API calls until feature works