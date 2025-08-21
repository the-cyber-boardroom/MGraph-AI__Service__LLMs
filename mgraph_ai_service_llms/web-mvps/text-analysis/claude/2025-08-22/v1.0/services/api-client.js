// mgraph_ai_service_llms/web-mvps/text-analysis/v1.0/services/api-client.js

export class APIClient {
    constructor(baseURL = '/platform/open-router/text-analysis') {
        this.baseURL = baseURL;
        this.cacheIds = new Map(); // Store cache IDs for all requests
    }

    // Individual analysis endpoints with cache_id capture
    async analyzeFacts(text) {
        const startTime = Date.now();

        const response = await fetch(`${this.baseURL}/facts`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });

        if (!response.ok) {
            throw new Error(`Facts API Error: ${response.status}`);
        }

        const data = await response.json();
        data.responseTime = Date.now() - startTime;

        // Store cache_id if present
        if (data.cache_id) {
            this.storeCacheId('facts', data.cache_id, text);
        }

        return data;
    }

    async analyzeDataPoints(text) {
        const startTime = Date.now();

        const response = await fetch(`${this.baseURL}/data-points`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });

        if (!response.ok) {
            throw new Error(`Data Points API Error: ${response.status}`);
        }

        const data = await response.json();
        data.responseTime = Date.now() - startTime;

        if (data.cache_id) {
            this.storeCacheId('dataPoints', data.cache_id, text);
        }

        return data;
    }

    async analyzeQuestions(text) {
        const startTime = Date.now();

        const response = await fetch(`${this.baseURL}/questions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });

        if (!response.ok) {
            throw new Error(`Questions API Error: ${response.status}`);
        }

        const data = await response.json();
        data.responseTime = Date.now() - startTime;

        if (data.cache_id) {
            this.storeCacheId('questions', data.cache_id, text);
        }

        return data;
    }

    async analyzeHypotheses(text) {
        const startTime = Date.now();

        const response = await fetch(`${this.baseURL}/hypotheses`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });

        if (!response.ok) {
            throw new Error(`Hypotheses API Error: ${response.status}`);
        }

        const data = await response.json();
        data.responseTime = Date.now() - startTime;

        if (data.cache_id) {
            this.storeCacheId('hypotheses', data.cache_id, text);
        }

        return data;
    }

    // Combined analysis endpoint (legacy support from v1)
    async analyzeAll(text) {
        const startTime = Date.now();

        try {
            const response = await fetch(`${this.baseURL}/analyze-all`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.status}`);
            }

            const data = await response.json();
            const responseTime = Date.now() - startTime;

            return {
                ...data,
                responseTime,
                fromCache: responseTime < 500
            };
        } catch (error) {
            console.error('API Error:', error);
            // Return mock data for demo purposes
            return this.getMockData(text);
        }
    }

    // Cache inspection methods
    async getCacheEntry(cacheId) {
        const response = await fetch(`/platform/open-router/chat/cache-entry/${cacheId}`);

        if (!response.ok) {
            throw new Error(`Cache retrieval error: ${response.status}`);
        }

        return await response.json();
    }

    async getCacheStats() {
        const response = await fetch('/cache/stats');

        if (!response.ok) {
            throw new Error(`Cache stats error: ${response.status}`);
        }

        return await response.json();
    }

    // Helper to store cache IDs with metadata
    storeCacheId(type, cacheId, text) {
        const entry = {
            type,
            cacheId,
            text: text.substring(0, 100) + (text.length > 100 ? '...' : ''),
            timestamp: new Date().toISOString()
        };

        this.cacheIds.set(`${type}-${Date.now()}`, entry);

        // Emit event for UI updates
        window.dispatchEvent(new CustomEvent('cache-id-captured', {
            detail: entry
        }));
    }

    // Get all captured cache IDs
    getAllCacheIds() {
        return Array.from(this.cacheIds.values());
    }

    // LLM completion endpoints
    async generateAnswer(question, systemPrompt) {
        const response = await fetch('/platform/open-router/llm-simple/complete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                user_prompt: question,
                system_prompt: systemPrompt,
                model: 'gpt-oss-120b',
                provider: 'groq'
            })
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }

        const data = await response.json();

        // Store cache_id if present
        if (data.cache_id) {
            this.storeCacheId('answer', data.cache_id, question);
        }

        return data;
    }

    // Smart deduplication using LLM
    async deduplicateItems(existing, newItems) {
        const systemPrompt = `You are a deduplication assistant. Given a list of existing items and new items, identify which new items are truly unique (not duplicates or near-duplicates of existing items).

Return ONLY a JSON array of unique items. Be strict - if items express the same concept with different wording, consider them duplicates.`;

        const userPrompt = `Existing items:
${existing.map((item, i) => `${i+1}. ${item}`).join('\n')}

New items to check:
${newItems.map((item, i) => `${i+1}. ${item}`).join('\n')}

Return only truly unique new items as a JSON array.`;

        const response = await fetch('/platform/open-router/llm-simple/complete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                user_prompt: userPrompt,
                system_prompt: systemPrompt,
                model: 'gpt-oss-120b',
                provider: 'groq'
            })
        });

        if (!response.ok) {
            throw new Error(`Deduplication API Error: ${response.status}`);
        }

        const data = await response.json();

        if (data.cache_id) {
            this.storeCacheId('deduplication', data.cache_id, 'dedup-operation');
        }

        try {
            const uniqueItems = JSON.parse(data.response_text);
            return { unique_items: [...existing, ...uniqueItems] };
        } catch (error) {
            return { unique_items: [...existing, ...newItems] };
        }
    }

    // Generate executive summary
    async generateSummary(globalData) {
        const systemPrompt = `You are a business analyst creating an executive summary. Synthesize the provided facts, data points, questions, and hypotheses into a concise, insightful summary.

Focus on:
1. Key findings and patterns
2. Critical data points
3. Most important questions to address
4. Most likely hypotheses

Keep the summary to 2-3 paragraphs maximum.`;

        const userPrompt = `Please create an executive summary from the following analysis:

Facts (${globalData.facts.length}):
${globalData.facts.slice(0, 10).join('\n')}

Data Points (${globalData.data_points.length}):
${globalData.data_points.slice(0, 10).join('\n')}

Key Questions (${globalData.questions.length}):
${globalData.questions.slice(0, 5).join('\n')}

Hypotheses (${globalData.hypotheses.length}):
${globalData.hypotheses.slice(0, 5).join('\n')}`;

        const response = await fetch('/platform/open-router/llm-simple/complete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                user_prompt: userPrompt,
                system_prompt: systemPrompt,
                model: 'gpt-oss-120b',
                provider: 'groq'
            })
        });

        if (!response.ok) {
            throw new Error(`Summary API Error: ${response.status}`);
        }

        const data = await response.json();

        if (data.cache_id) {
            this.storeCacheId('summary', data.cache_id, 'executive-summary');
        }

        return { summary_text: data.response_text, cache_id: data.cache_id };
    }

    // Mock data for testing/demo purposes
    getMockData(text) {
        const sentences = text.split('.').filter(s => s.trim().length > 0);
        const facts = sentences.slice(0, Math.min(4, sentences.length));

        return {
            text: text,
            facts: facts.map(f => f.trim() + '.'),
            data_points: [
                "Q3 revenue: $5.2 million",
                "30% year-over-year increase",
                "50 new employees by December",
                "Focus on engineering and sales"
            ],
            questions: [
                "What factors contributed to this growth?",
                "How does this compare to industry standards?",
                "What are the long-term projections?",
                "What challenges might arise?",
                "How will resources be allocated?"
            ],
            hypotheses: [
                "The organization is experiencing rapid expansion",
                "Market conditions are favorable for growth",
                "Strategic investments are paying off",
                "Competitive advantage is being established"
            ],
            summary: {
                facts_count: facts.length,
                data_points_count: 4,
                questions_count: 5,
                hypotheses_count: 4
            },
            responseTime: 250,
            fromCache: false,
            model: "mock-model",
            provider: "mock"
        };
    }
}