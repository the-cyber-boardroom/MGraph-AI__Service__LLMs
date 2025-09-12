# Text Analysis API Technical Briefing Document

## Introduction

This document provides comprehensive technical documentation for a text analysis API service that offers advanced natural language processing capabilities. The API is designed to extract structured information from unstructured text input, enabling applications to automatically identify facts, data points, generate relevant questions, and formulate hypotheses based on textual content.

The API service operates on a RESTful architecture, accepting POST requests with JSON payloads and returning structured JSON responses. All endpoints are served from the base URL `/platform/open-router/text-analysis/` and utilize the same underlying language model infrastructure (openai/gpt-oss-120b via groq provider) to ensure consistency across different analysis types.

Key features of this API include:
- **Fact Extraction**: Identifies and isolates discrete factual statements from input text
- **Data Point Identification**: Extracts quantifiable metrics and measurable information
- **Question Generation**: Creates relevant follow-up questions based on the content
- **Hypothesis Formation**: Generates potential interpretations and predictions based on the information
- **Comprehensive Analysis**: Combines all analysis types in a single request for efficiency

The API is particularly suited for applications in business intelligence, content analysis, automated reporting, research assistance, and data-driven decision making. Each endpoint is optimized for specific use cases while maintaining a consistent interface pattern for ease of integration.

## API Methods Overview

| Endpoint | Method | Purpose | Response Fields | Use Case |
|----------|--------|---------|-----------------|----------|
| `/text-analysis/facts` | POST | Extract factual statements from text | `facts[]`, `facts_count`, `model`, `provider` | Fact-checking, content verification, knowledge extraction |
| `/text-analysis/data-points` | POST | Identify quantifiable metrics and data | `data_points[]`, `data_points_count`, `model`, `provider` | Business metrics tracking, KPI extraction, report analysis |
| `/text-analysis/questions` | POST | Generate relevant follow-up questions | `questions[]`, `questions_count`, `model`, `provider` | Research assistance, interview preparation, content gaps analysis |
| `/text-analysis/hypotheses` | POST | Create hypotheses based on content | `hypotheses[]`, `hypotheses_count`, `model`, `provider` | Strategic planning, prediction modeling, trend analysis |
| `/text-analysis/analyze-all` | POST | Perform comprehensive analysis | All fields from above endpoints plus `summary{}` | Complete content analysis, comprehensive reporting |

## Detailed API Specifications

### 1. Facts Extraction Endpoint

**Endpoint:** `/text-analysis/facts`  
**Method:** POST  
**Content-Type:** application/json

#### Request Structure
```bash
curl -X 'POST' \
  'http://0.0.0.0:10011/platform/open-router/text-analysis/facts' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "The company reported Q3 revenue of $5.2 million, a 30% increase year-over-year. CEO Jane Smith announced plans to hire 50 new employees by December."
  }'
```

#### Request Body Schema
```json
{
  "text": "string"  // Required: The text to analyze for factual statements
}
```

#### Response Structure
```json
{
  "text": "The company reported Q3 revenue of $5.2 million, a 30% increase year-over-year. CEO Jane Smith announced plans to hire 50 new employees by December.",
  "facts": [
    "The company reported Q3 revenue of $5.2 million.",
    "The Q3 revenue was a 30% increase year-over-year.",
    "The CEO is Jane Smith.",
    "Jane Smith announced plans to hire 50 new employees by December."
  ],
  "facts_count": 4,
  "model": "openai/gpt-oss-120b",
  "provider": "groq"
}
```

#### Response Fields
- `text` (string): Echo of the input text
- `facts` (array[string]): List of extracted factual statements
- `facts_count` (integer): Total number of facts extracted
- `model` (string): AI model used for processing
- `provider` (string): Model provider service

### 2. Data Points Extraction Endpoint

**Endpoint:** `/text-analysis/data-points`  
**Method:** POST  
**Content-Type:** application/json

#### Request Structure
```bash
curl -X 'POST' \
  'http://0.0.0.0:10011/platform/open-router/text-analysis/data-points' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "The company reported Q3 revenue of $5.2 million, a 30% increase year-over-year. CEO Jane Smith announced plans to hire 50 new employees by December."
  }'
```

#### Request Body Schema
```json
{
  "text": "string"  // Required: The text to analyze for data points
}
```

#### Response Structure
```json
{
  "text": "The company reported Q3 revenue of $5.2 million, a 30% increase year-over-year. CEO Jane Smith announced plans to hire 50 new employees by December.",
  "data_points": [
    "Q3 revenue: $5.2 million",
    "30% year-over-year increase",
    "Hire 50 new employees by December"
  ],
  "data_points_count": 3,
  "model": "openai/gpt-oss-120b",
  "provider": "groq"
}
```

#### Response Fields
- `text` (string): Echo of the input text
- `data_points` (array[string]): List of extracted quantifiable data points
- `data_points_count` (integer): Total number of data points extracted
- `model` (string): AI model used for processing
- `provider` (string): Model provider service

### 3. Question Generation Endpoint

**Endpoint:** `/text-analysis/questions`  
**Method:** POST  
**Content-Type:** application/json

#### Request Structure
```bash
curl -X 'POST' \
  'http://0.0.0.0:10011/platform/open-router/text-analysis/questions' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "The company reported Q3 revenue of $5.2 million, a 30% increase year-over-year. CEO Jane Smith announced plans to hire 50 new employees by December."
  }'
```

#### Request Body Schema
```json
{
  "text": "string"  // Required: The text to generate questions from
}
```

#### Response Structure
```json
{
  "text": "The company reported Q3 revenue of $5.2 million, a 30% increase year-over-year. CEO Jane Smith announced plans to hire 50 new employees by December.",
  "questions": [
    "What factors contributed to the 30% year-over-year revenue increase in Q3?",
    "Can you provide details on the profit margins or net income for the same period?",
    "Which departments or functions will the 50 new hires be allocated to?",
    "What is the budget allocated for the hiring initiative and associated training costs?",
    "How does the company plan to sustain this revenue growth in the upcoming quarters?",
    "Are there any new products, services, or market expansions driving the revenue boost?",
    "What metrics will be used to assess the success of the hiring plan by December?"
  ],
  "questions_count": 7,
  "model": "openai/gpt-oss-120b",
  "provider": "groq"
}
```

#### Response Fields
- `text` (string): Echo of the input text
- `questions` (array[string]): List of generated follow-up questions
- `questions_count` (integer): Total number of questions generated
- `model` (string): AI model used for processing
- `provider` (string): Model provider service

### 4. Hypothesis Generation Endpoint

**Endpoint:** `/text-analysis/hypotheses`  
**Method:** POST  
**Content-Type:** application/json

#### Request Structure
```bash
curl -X 'POST' \
  'http://0.0.0.0:10011/platform/open-router/text-analysis/hypotheses' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "The company reported Q3 revenue of $5.2 million, a 30% increase year-over-year. CEO Jane Smith announced plans to hire 50 new employees by December."
  }'
```

#### Request Body Schema
```json
{
  "text": "string"  // Required: The text to generate hypotheses from
}
```

#### Response Structure
```json
{
  "text": "The company reported Q3 revenue of $5.2 million, a 30% increase year-over-year. CEO Jane Smith announced plans to hire 50 new employees by December.",
  "hypotheses": [
    "The revenue growth may be driven by a successful new product launch or expanded market presence",
    "Hiring 50 new employees suggests the company is preparing for increased operational demand or new projects",
    "The company may be planning to enter new geographic markets or industry segments",
    "The CEO's announcement could be intended to boost investor confidence and signal strong future performance",
    "The hiring plan indicates that the company expects continued revenue growth and needs additional staff to sustain it",
    "The increase in revenue might be a result of higher demand for existing products or services",
    "The company could be positioning itself for a future fundraising round or strategic partnership"
  ],
  "hypotheses_count": 7,
  "model": "openai/gpt-oss-120b",
  "provider": "groq"
}
```

#### Response Fields
- `text` (string): Echo of the input text
- `hypotheses` (array[string]): List of generated hypotheses
- `hypotheses_count` (integer): Total number of hypotheses generated
- `model` (string): AI model used for processing
- `provider` (string): Model provider service

### 5. Comprehensive Analysis Endpoint

**Endpoint:** `/text-analysis/analyze-all`  
**Method:** POST  
**Content-Type:** application/json

#### Request Structure
```bash
curl -X 'POST' \
  'http://0.0.0.0:10011/platform/open-router/text-analysis/analyze-all' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "The company reported Q3 revenue of $5.2 million, a 30% increase year-over-year. CEO Jane Smith announced plans to hire 50 new employees by December."
  }'
```

#### Request Body Schema
```json
{
  "text": "string"  // Required: The text to perform comprehensive analysis on
}
```

#### Response Structure
```json
{
  "text": "The company reported Q3 revenue of $5.2 million, a 30% increase year-over-year. CEO Jane Smith announced plans to hire 50 new employees by December.",
  "facts": [
    "The company reported Q3 revenue of $5.2 million.",
    "The Q3 revenue was a 30% increase year-over-year.",
    "The CEO is Jane Smith.",
    "Jane Smith announced plans to hire 50 new employees by December."
  ],
  "data_points": [
    "Q3 revenue: $5.2 million",
    "30% year-over-year increase",
    "Hire 50 new employees by December"
  ],
  "questions": [
    "What factors contributed to the 30% year-over-year revenue increase in Q3?",
    "Can you provide details on the profit margins or net income for the same period?",
    "Which departments or functions will the 50 new hires be allocated to?",
    "What is the budget allocated for the hiring initiative and associated training costs?",
    "How does the company plan to sustain this revenue growth in the upcoming quarters?",
    "Are there any new products, services, or market expansions driving the revenue boost?",
    "What metrics will be used to assess the success of the hiring plan by December?"
  ],
  "hypotheses": [
    "The revenue growth may be driven by a successful new product launch or expanded market presence",
    "Hiring 50 new employees suggests the company is preparing for increased operational demand or new projects",
    "The company may be planning to enter new geographic markets or industry segments",
    "The CEO's announcement could be intended to boost investor confidence and signal strong future performance",
    "The hiring plan indicates that the company expects continued revenue growth and needs additional staff to sustain it",
    "The increase in revenue might be a result of higher demand for existing products or services",
    "The company could be positioning itself for a future fundraising round or strategic partnership"
  ],
  "summary": {
    "facts_count": 4,
    "data_points_count": 3,
    "questions_count": 7,
    "hypotheses_count": 7
  },
  "model": "openai/gpt-oss-120b",
  "provider": "groq"
}
```

#### Response Fields
- `text` (string): Echo of the input text
- `facts` (array[string]): List of extracted factual statements
- `data_points` (array[string]): List of extracted quantifiable data points
- `questions` (array[string]): List of generated follow-up questions
- `hypotheses` (array[string]): List of generated hypotheses
- `summary` (object): Count summary of all extracted elements
  - `facts_count` (integer): Total number of facts extracted
  - `data_points_count` (integer): Total number of data points extracted
  - `questions_count` (integer): Total number of questions generated
  - `hypotheses_count` (integer): Total number of hypotheses generated
- `model` (string): AI model used for processing
- `provider` (string): Model provider service

## Implementation Considerations

### Error Handling
While not shown in the examples, implementations should handle standard HTTP error codes:
- `400 Bad Request`: Invalid JSON or missing required fields
- `500 Internal Server Error`: Processing errors or model failures
- `503 Service Unavailable`: Service temporarily unavailable

### Rate Limiting
Consider implementing rate limiting to prevent abuse. Typical patterns might include:
- Per-minute request limits
- Token-based authentication for higher limits
- Concurrent request limitations

### Performance Optimization
- The `/analyze-all` endpoint is more efficient for comprehensive analysis than calling individual endpoints, but it will take longer, so it will be better to call each type of analysis individually (in parallel, with the FastAPI server supports)

### Security Considerations
- Validate and sanitize input text to prevent injection attacks
- Implement appropriate authentication mechanisms
- Use HTTPS in production environments
- Consider implementing request size limits to prevent DoS attacks

### Integration Best Practices
1. Always handle the echo of input text in responses for validation
2. Use the count fields for quick statistics without parsing arrays
3. Leverage the model and provider fields for debugging and monitoring

## Conclusion

This text analysis API provides a robust foundation for building applications that require intelligent text processing capabilities. The consistent interface pattern across all endpoints, combined with the comprehensive `/analyze-all` endpoint, offers flexibility for various use cases while maintaining simplicity in implementation. The structured JSON responses enable easy integration with downstream systems and provide clear, actionable insights from unstructured text data.