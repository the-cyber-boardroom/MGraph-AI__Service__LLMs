export class APIClient {
    constructor(baseURL = '/platform/open-router/text-analysis') {
        this.baseURL = baseURL;
    }

    // Individual analysis endpoints for parallel calls
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
        return data;
    }

    // LLM endpoints
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

        return await response.json();
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
        try {
            const uniqueItems = JSON.parse(data.response_text);
            return { unique_items: [...existing, ...uniqueItems] };
        } catch (error) {
            // If parsing fails, return all items
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
        return { summary_text: data.response_text };
    }
}