# Text Analyzer v1.0

A comprehensive text analysis web application that extracts facts, data points, questions, and hypotheses from any text input.

## Features

- **Multi-view Interface**: Chat view, Analysis dashboard, and LLM request inspector
- **Parallel Processing**: Simultaneous API calls for faster analysis
- **Cache Management**: Full cache ID tracking and inspection
- **Smart Deduplication**: AI-powered deduplication of similar items
- **Global & Local Views**: Aggregate analysis across multiple texts
- **Executive Summaries**: AI-generated summaries of all analyses
- **Question Generation**: Automatic question generation with inline answers
- **Activity Logging**: Real-time activity tracking with clickable cache IDs

## Directory Structure

```
v1.0/
├── index.html                          # Main entry point
├── css/
│   └── main.css                       # Global styles
├── components/
│   ├── text-analyzer/
│   │   ├── text-analyzer.js          # Main orchestrator component
│   │   └── text-analyzer.css         # Component styles
│   ├── chat-panel/
│   │   ├── chat-panel.js             # Chat interface
│   │   └── chat-panel.css            # Component styles
│   ├── analysis-panel/
│   │   ├── analysis-panel.js         # Analysis display
│   │   └── analysis-panel.css        # Component styles
│   ├── activity-log/
│   │   ├── activity-log.js           # Activity tracker
│   │   └── activity-log.css          # Component styles
│   ├── analysis-dashboard/
│   │   ├── analysis-dashboard.js     # Dashboard view
│   │   └── analysis-dashboard.css    # Component styles
│   └── llm-request-viewer/
│       ├── llm-request-viewer.js     # Cache inspector
│       └── llm-request-viewer.css    # Component styles
├── services/
│   └── api-client.js                 # API communication service
├── utils/
│   ├── text-formatter.js             # Text formatting utilities
│   └── sample-texts.js               # Sample text data
└── README.md                          # This file
```

## Installation

1. Clone or download the v1.0 directory to your web server
2. Ensure the application is served from a web server (not file://)
3. Configure API endpoints if needed (see Configuration section)

## Configuration

### API Endpoints

The default API endpoints are configured in `services/api-client.js`:

```javascript
// Default base URL
const baseURL = '/platform/open-router/text-analysis'
```

To use a different API endpoint, modify the constructor in `api-client.js`:

```javascript
constructor(baseURL = 'https://your-api-endpoint.com/text-analysis') {
    this.baseURL = baseURL;
}
```

### Supported Models

The application uses the following models by default:
- Model: `gpt-oss-120b`
- Provider: `groq`

These can be configured in the API client methods.

## Usage

### Basic Text Analysis

1. Open the application in a web browser
2. Enter or paste text in the chat input area
3. Click "Analyze" or press Enter
4. View results in the Analysis panel

### Sample Texts

Click the "Sample" button to load pre-configured sample texts for testing.

### View Modes

- **Chat View**: Default view for text input and conversation
- **Analysis View**: Dashboard with aggregated metrics and search
- **LLM Requests**: Inspect cached API requests and responses

### Keyboard Shortcuts

- `Ctrl+Shift+C`: Open LLM Request Viewer
- `Enter`: Send message (in chat input)
- `Shift+Enter`: New line (in chat input)

## API Requirements

The application expects the following API endpoints:

### Analysis Endpoints
- `POST /text-analysis/facts` - Extract facts from text
- `POST /text-analysis/data-points` - Extract data points
- `POST /text-analysis/questions` - Generate questions
- `POST /text-analysis/hypotheses` - Generate hypotheses

### LLM Endpoint
- `POST /llm-simple/complete` - Generate text completions

### Cache Endpoints
- `GET /chat/cache-entry/{cacheId}` - Retrieve cached request
- `GET /cache/stats` - Get cache statistics

## Browser Compatibility

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Development

### Running Locally

```bash
# Using Python
python -m http.server 8000

# Using Node.js
npx http-server -p 8000

# Using PHP
php -S localhost:8000
```

Then open `http://localhost:8000/v1.0/` in your browser.

### Component Architecture

Each component is self-contained with its own:
- JavaScript class extending `HTMLElement`
- CSS file for styling
- Event communication via CustomEvents

### Adding New Components

1. Create a new folder in `components/`
2. Add the component JS and CSS files
3. Import and register in `index.html`
4. Add styles link in `index.html`

## Features in Detail

### Cache ID Tracking

All API requests generate cache IDs that are:
- Displayed in the UI for each analysis
- Clickable to inspect full request/response
- Tracked in the activity log
- Available in the LLM Request Viewer

### Smart Deduplication

When multiple texts are analyzed, the system:
- Uses AI to identify duplicate or similar items
- Maintains unique lists in global view
- Preserves all original data in local views

### Question Generation

For each analysis, the system:
- Generates relevant questions about the text
- Allows inline answer generation
- Supports adding questions to chat input
- Tracks cache IDs for all generated answers

## Troubleshooting

### API Connection Issues

If the API is not available:
- The application will show warnings in the console
- Mock data will be used for demonstration
- Check network tab for failed requests

### Cache Inspection Errors

If cache entries cannot be loaded:
- Verify the cache ID is valid
- Check if the entry has expired
- Ensure API endpoint is accessible

## License

[Your License Here]

## Support

For issues or questions, please contact [Your Contact Info]