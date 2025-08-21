# Text Analysis v0.3 - Analysis Tracking

## Overview
Introduces global/local analysis tracking with the ability to maintain cumulative insights across multiple text analyses.

## Major Features
- **Multiple Analysis Support**: Track unlimited text analyses in one session
- **Global View**: Combined, deduplicated insights from all analyses
- **Local View**: Individual analysis details with navigation
- **Clickable Analysis Summaries**: Jump between analyses from chat
- **Smart Deduplication**: Automatic removal of duplicate insights

## New Components
- **Analysis Navigation**: Switch between global and individual views
- **Analysis Counter**: Track analysis numbers (#1, #2, etc.)
- **View Toggle**: Easy switching between global/local perspectives
- **Text Preview**: Shows analyzed text snippet in local view

## Data Management
- **In-Memory Storage**: All analyses stored in Map structure
- **Set-Based Deduplication**: Global data uses Sets for uniqueness
- **Analysis Metadata**: Timestamp, ID, text, and analysis number

## UI Enhancements
- **Analysis Messages**: Distinct yellow cards with analysis summaries
- **Cache Summary**: Overview of all cached requests
- **Global Statistics**: Combined counts across all analyses
- **Click Navigation**: Click any analysis message to view details

## File Structure
```
v0.3/
├── index.html
├── css/
│   └── styles.css (imports v0.2 styles)
└── js/
    ├── components/
    │   ├── text-analyzer-v3.js
    │   ├── chat-panel-v3.js
    │   └── analysis-panel-v3.js
    └── utils/
        └── api-client-v2.js (reused)
```

## Usage Flow
1. Analyze multiple texts sequentially
2. Each analysis gets a numbered card in chat
3. Click cards to view individual analysis
4. Use "Global View" button for combined insights
5. All unique items automatically deduplicated

## Technical Details
- Analysis IDs: `analysis-{counter}`
- Global deduplication using Set operations
- Persistent view state during session
- Event-driven architecture for view changes