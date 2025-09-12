# Technical Briefing: Text Analysis API for UI Development

## API Overview

The Text Analysis API provides structured extraction of information from unstructured text through five specialized endpoints. The service uses OpenRouter's LLM infrastructure (defaulting to GROQ provider for speed) to analyze text and return structured JSON responses.

**Base URL:** `/text-analysis/`

## Endpoints

### 1. Extract Facts
**POST** `/text-analysis/facts`

Extracts concrete, verifiable facts from the provided text.

**Request Body:**
```json
{
  "text": "string (required) - The text to analyze"
}
```

**Response (200 OK):**
```json
{
  "text": "string - Original input text",
  "facts": ["array of strings - Each element is a distinct fact"],
  "facts_count": "integer - Number of facts extracted",
  "model": "string - LLM model used (openai/gpt-oss-120b)",
  "provider": "string - Provider used (typically 'groq')"
}
```

**Example Facts:**
- "The meeting is scheduled for 3pm on Friday"
- "Revenue increased by 25% in Q4"
- "John Smith is the project manager"

### 2. Extract Data Points
**POST** `/text-analysis/data-points`

Extracts quantifiable metrics, numbers, dates, and measurements.

**Request/Response Structure:** Same as facts endpoint

**Response Specifics:**
```json
{
  "data_points": ["array of quantifiable data"],
  "data_points_count": "integer"
}
```

**Example Data Points:**
- "$5.2 million in Q3 revenue"
- "30% year-over-year increase"
- "50 new employees by December"
- "Response time: 150ms (p95: 300ms)"

### 3. Generate Questions
**POST** `/text-analysis/questions`

Generates relevant follow-up questions based on the text content.

**Response Specifics:**
```json
{
  "questions": ["array of questions to ask the user"],
  "questions_count": "integer"
}
```

**Example Questions:**
- "What were the primary factors driving the revenue increase?"
- "How will the new hires be distributed across departments?"
- "What is the timeline for addressing the performance issues?"

### 4. Generate Hypotheses
**POST** `/text-analysis/hypotheses`

Creates logical inferences and educated assumptions based on the text.

**Response Specifics:**
```json
{
  "hypotheses": ["array of inferred statements"],
  "hypotheses_count": "integer"
}
```

**Example Hypotheses:**
- "The revenue growth suggests successful market expansion"
- "Hiring plans indicate anticipated business growth"
- "Performance issues may be related to increased user load"

### 5. Comprehensive Analysis
**POST** `/text-analysis/analyze-all`

Runs all four analysis types in a single request.

**Response (200 OK):**
```json
{
  "text": "string - Original input",
  "facts": ["array of facts"],
  "data_points": ["array of data points"],
  "questions": ["array of questions"],
  "hypotheses": ["array of hypotheses"],
  "summary": {
    "facts_count": "integer",
    "data_points_count": "integer",
    "questions_count": "integer",
    "hypotheses_count": "integer"
  },
  "model": "string",
  "provider": "string"
}
```

## UI Design Considerations

### Input Component
- **Text Area**: Multi-line input field for text (recommended min height: 150px)
- **Character Counter**: Service handles up to ~8000 characters effectively
- **Sample Text Button**: Pre-fill with example text for demonstration
- **Clear Button**: Reset the input field

### Output Display

#### Tabbed Interface Recommended
Create tabs for each analysis type:
1. **Facts Tab**: Display as bullet list or cards
2. **Data Points Tab**: Consider highlighting numbers/percentages in different color
3. **Questions Tab**: Display as numbered list with optional "Copy" button per question
4. **Hypotheses Tab**: Display as expandable cards or accordion
5. **All Analysis Tab**: Combined view with collapsible sections

#### Visual Indicators
- **Loading State**: Show spinner during API call (typical response time: 1-3 seconds)
- **Count Badges**: Display count next to each tab (e.g., "Facts (5)")
- **Empty State**: Handle cases where no items are extracted
- **Error State**: Display user-friendly message if API fails

### Interactive Features

1. **Copy to Clipboard**: Individual items or entire lists
2. **Export Options**: JSON, CSV, or formatted text
3. **Filter/Search**: For results with many items
4. **Highlight Source**: Show which part of input text relates to each extracted item (client-side matching)

### Performance Considerations

- **Response Times**: 
  - Typical: 1-2 seconds
  - Complex text: 2-4 seconds
  - Cache hits: <500ms

- **Rate Limiting**: No explicit limits, but recommend:
  - Debounce input (wait 500ms after typing stops)
  - Disable submit during processing
  - Client-side text length validation (<10,000 chars)

### Error Handling

**Common Error Responses:**
- `500`: LLM processing error (retry with exponential backoff)
- `422`: Invalid request format
- `503`: Service temporarily unavailable

**Error Response Format:**
```json
{
  "detail": "string - Error description"
}
```

### Best Practices for UI

1. **Progressive Disclosure**: Start with `/analyze-all`, let users drill into specific types
2. **Visual Hierarchy**: Use different colors/icons for each analysis type
3. **Responsive Design**: Stack tabs vertically on mobile
4. **Accessibility**: 
   - ARIA labels for screen readers
   - Keyboard navigation for tabs
   - High contrast mode support

### Example UI Flow

```
1. User enters/pastes text
2. Clicks "Analyze" button
3. UI shows loading spinner
4. API call to /analyze-all
5. Results displayed in tabs
6. User can:
   - Switch between tabs
   - Copy individual items
   - Export all results
   - Modify text and re-analyze
```

### Caching Strategy

The API implements server-side caching. For the UI:
- Identical text will return cached results (faster response)
- Consider client-side caching for tab switching
- Clear cache on new text input

### Mobile Considerations

- **Minimum viewport**: 320px width
- **Touch targets**: 44x44px minimum for buttons
- **Collapsible sections**: Essential for mobile view
- **Swipe gestures**: Optional for tab navigation

This API is stateless and requires no authentication. All text processing happens server-side with no data persistence beyond caching.