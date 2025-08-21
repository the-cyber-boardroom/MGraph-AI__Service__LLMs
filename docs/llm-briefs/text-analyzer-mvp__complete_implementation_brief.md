# Text Analyzer MVP - Complete Implementation Brief

## Overview
Build a text analysis interface with chat functionality that integrates with the MGraph-AI__Service__LLMs text analysis endpoints. The interface consists of a chat panel for conversational interaction and an analysis panel that displays extracted facts, data points, questions, and hypotheses from the conversation.

## Architecture Requirements
- Pure vanilla JavaScript with Web Components (HTMLElement)
- No external framework dependencies
- CSS in separate files
- Common JavaScript utilities in separate modules
- All files served via FastAPI static routes (no CORS issues)
- Cache-aware with visual indicators

## File Structure Required
```
admin_ui/static/
├── css/
│   ├── text-analyzer.css        # Main container styles
│   ├── chat-panel.css          # Chat interface styles
│   └── analysis-panel.css      # Analysis results styles
├── js/
│   ├── utils/
│   │   ├── api-client.js       # API communication
│   │   ├── text-formatter.js   # Text processing utilities
│   │   └── sample-texts.js     # Default sample content
│   └── components/
│       ├── text-analyzer.js    # Main container component
│       ├── chat-panel.js       # Chat interface component
│       └── analysis-panel.js   # Analysis display component
└── html/
    └── text-analyzer.html       # Entry point HTML

```

## API Endpoints Available
```
Base URL: /text-analysis/
- POST /facts - Extract facts from text
- POST /data-points - Extract data points
- POST /questions - Generate questions
- POST /hypotheses - Generate hypotheses
- POST /analyze-all - Comprehensive analysis (USE THIS FOR MVP)

Request format:
{
  "text": "string"
}

Response format (from analyze-all):
{
  "text": "original text",
  "facts": ["array of facts"],
  "data_points": ["array of data points"],
  "questions": ["array of questions"],
  "hypotheses": ["array of hypotheses"],
  "summary": {
    "facts_count": number,
    "data_points_count": number,
    "questions_count": number,
    "hypotheses_count": number
  },
  "model": "openai/gpt-oss-120b",
  "provider": "groq"
}
```

## File Specifications

### 1. text-analyzer.html
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Text Analyzer</title>
    <link rel="stylesheet" href="/admin/admin-static/serve-css/text-analyzer.css">
</head>
<body>
    <text-analyzer></text-analyzer>
    
    <script type="module">
        import { TextAnalyzer } from '/admin/admin-static/serve-js/components/text-analyzer.js';
        import { ChatPanel } from '/admin/admin-static/serve-js/components/chat-panel.js';
        import { AnalysisPanel } from '/admin/admin-static/serve-js/components/analysis-panel.js';
        
        // Register custom elements
        customElements.define('text-analyzer', TextAnalyzer);
        customElements.define('chat-panel', ChatPanel);
        customElements.define('analysis-panel', AnalysisPanel);
    </script>
</body>
</html>
```

### 2. text-analyzer.js (Main Container)
This component should:
- Create a two-panel layout (chat left, analysis right)
- Coordinate communication between chat and analysis panels
- Load and inject CSS dynamically
- Handle the main analysis workflow

Key methods needed:
- `async loadCSS()` - Load and inject the CSS file
- `render()` - Create the main layout with chat-panel and analysis-panel
- `async analyzeText(text)` - Call the analyze-all endpoint
- `handleQuestionClick(question)` - Add question to chat and trigger analysis
- `updateAnalysisDisplay(data)` - Update the analysis panel with new results

### 3. chat-panel.js
This component should:
- Display a chat interface with message history
- Include input field and send button
- Auto-populate with sample text on first load
- Maintain conversation history
- Emit events when new messages are sent

Structure:
```javascript
class ChatPanel extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        this.messages = [];
        this.isFirstLoad = true;
    }
    
    // Required methods:
    // - loadCSS() - Load chat-panel.css
    // - render() - Create chat UI
    // - addMessage(text, sender='user') - Add message to chat
    // - loadSampleText() - Load initial sample
    // - handleSend() - Process message send
    // - scrollToBottom() - Auto-scroll chat
}
```

Features:
- Message bubbles (differentiate user vs system)
- Timestamp for each message
- Auto-scroll to latest message
- Clear chat button
- Character count indicator

### 4. analysis-panel.js
This component should:
- Display analysis results in tabs
- Show count badges for each category
- Make questions clickable
- Include copy functionality
- Show cache/response time indicators

Tabs required:
- Facts (bullet list)
- Data Points (highlighted cards)
- Questions (clickable list)
- Hypotheses (expandable cards)
- Summary (overview stats)

Key features:
- Click on any question to send it to chat
- Copy button for each section
- Visual indicator for cached vs fresh results
- Loading state during analysis

### 5. api-client.js (Utility)
```javascript
export class APIClient {
    constructor(baseURL = '/text-analysis') {
        this.baseURL = baseURL;
    }
    
    async analyzeAll(text) {
        const response = await fetch(`${this.baseURL}/analyze-all`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });
        return await response.json();
    }
    
    // Add methods for individual endpoints if needed
}
```

### 6. text-formatter.js (Utility)
```javascript
export class TextFormatter {
    static truncate(text, maxLength = 100) {
        return text.length > maxLength 
            ? text.substring(0, maxLength) + '...' 
            : text;
    }
    
    static highlightNumbers(text) {
        // Highlight numbers and percentages
        return text.replace(/(\d+\.?\d*%?)/g, '<span class="highlight">$1</span>');
    }
    
    static formatTimestamp(date) {
        return new Intl.DateTimeFormat('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        }).format(date);
    }
}
```

### 7. sample-texts.js (Utility)
```javascript
export const SAMPLE_TEXTS = {
    default: "The company reported Q3 revenue of $5.2 million, a 30% increase year-over-year. CEO Jane Smith announced plans to hire 50 new employees by December. The expansion focuses on the engineering and sales departments, with a particular emphasis on AI and machine learning expertise. Market analysts predict continued growth through Q4, citing strong product adoption and customer retention rates.",
    
    technical: "The new API endpoint processes requests in under 100ms with a 99.9% uptime SLA. It supports both REST and GraphQL protocols, handling up to 10,000 concurrent connections. The system uses Redis for caching with a 15-minute TTL and PostgreSQL for persistent storage.",
    
    product: "Our latest product release includes five major features requested by enterprise customers. Beta testing showed a 40% improvement in user engagement and a 25% reduction in support tickets. The rollout plan targets 1000 users in week one, scaling to full deployment by month end."
};
```

## CSS Requirements

### text-analyzer.css
- Grid layout for two panels (60% chat, 40% analysis)
- Responsive breakpoint at 1024px (stack vertically)
- Consistent color scheme matching OSBot-Fast-API admin UI
- Use CSS variables for theming

### chat-panel.css
- Message bubbles with sender differentiation
- Smooth scrolling
- Input area stuck to bottom
- Loading indicators
- Max height with scroll

### analysis-panel.css
- Tab navigation
- Count badges
- Clickable questions with hover effect
- Copy button styling
- Cache indicator badge

## Interaction Flow

1. **Initial Load**
   - Chat panel loads with welcome message
   - Sample text auto-populated in input
   - User clicks "Analyze" or presses Enter
   - Analysis runs, results appear in right panel

2. **Question Interaction**
   - User clicks a question in analysis panel
   - Question appears in chat input
   - User can edit or send as-is
   - Response generates new analysis
   - Both panels update

3. **Continuous Analysis**
   - Each message exchange is analyzed
   - Results accumulate in analysis panel
   - Previous analyses remain accessible
   - Clear option to reset conversation

## Event Flow
```
User types → ChatPanel → 'message-sent' event → TextAnalyzer
TextAnalyzer → API call → 'analysis-complete' event → AnalysisPanel
AnalysisPanel → 'question-clicked' event → ChatPanel
```

## Visual Requirements

### Color Scheme (matching OSBot-Fast-API)
```css
:root {
    --color-primary: #667eea;
    --color-primary-dark: #5a67d8;
    --color-success: #48bb78;
    --color-warning: #ed8936;
    --color-info: #4299e1;
    --bg-primary: #ffffff;
    --bg-secondary: #f8f9fa;
    --text-primary: #212529;
    --text-secondary: #495057;
    --border-color: #dee2e6;
}
```

### Loading States
- Spinner during API calls
- Skeleton loaders for content areas
- Disabled state for buttons during processing

### Cache Indicators
- Green badge for cached results (<500ms)
- Blue badge for fresh results
- Display response time

## Error Handling

1. **API Errors**
   - Show user-friendly error messages
   - Retry button for failed requests
   - Fallback to cached results if available

2. **Validation**
   - Minimum text length (10 characters)
   - Maximum text length (8000 characters)
   - Empty input prevention

3. **Edge Cases**
   - Handle empty analysis results
   - Long text truncation in display
   - Network timeout handling

## Testing Checklist

- [ ] Sample text loads and analyzes correctly
- [ ] Questions are clickable and populate chat
- [ ] Analysis accumulates across conversation
- [ ] Copy buttons work for all sections
- [ ] Cache indicators display correctly
- [ ] Responsive design works on mobile
- [ ] Error states handle gracefully
- [ ] Loading states show appropriately
- [ ] Tab switching preserves state
- [ ] Clear/reset functionality works

## Browser Compatibility
- Modern browsers (Chrome, Firefox, Safari, Edge)
- ES6+ JavaScript features
- CSS Grid and Flexbox
- Web Components support

## Security Considerations
- Sanitize all user input before display
- Escape HTML in chat messages
- No localStorage/sessionStorage usage
- API calls only to same-origin endpoints

This completes the specification for the Text Analyzer MVP. Each file should be created following these specifications, maintaining consistency with the existing OSBot-Fast-API admin UI patterns.