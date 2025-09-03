// Extend the v1.0 API client to support context
import { APIClient as BaseAPIClient } from '../../../2025-08-22/v1.0/services/api-client.js';

export class APIClient extends BaseAPIClient {

    // Add methods that include context in the prompts
    async analyzeFactsWithContext(text, context = '') {
        const startTime = Date.now();

        // Prepend context to the text for analysis
        const contextualText = context + text;

        const response = await fetch(`${this.baseURL}/facts`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: contextualText,
                // Or pass context separately if API supports it
                // context: context
            })
        });

        if (!response.ok) {
            throw new Error(`Facts API Error: ${response.status}`);
        }

        const data = await response.json();
        data.responseTime = Date.now() - startTime;

        if (data.cache_id) {
            this.storeCacheId('facts', data.cache_id, text);
        }

        return data;
    }

    // Similar methods for other analysis types
    async analyzeDataPointsWithContext(text, context = '') {
        const contextualText = context + text;
        return this.analyzeDataPoints(contextualText);
    }

    async analyzeQuestionsWithContext(text, context = '') {
        const contextualText = context + text;
        return this.analyzeQuestions(contextualText);
    }

    async analyzeHypothesesWithContext(text, context = '') {
        const contextualText = context + text;
        return this.analyzeHypotheses(contextualText);
    }
}