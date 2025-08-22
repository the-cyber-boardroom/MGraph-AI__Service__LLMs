export class APIClient {
    constructor(baseURL = '/platform/open-router/text-analysis') {
        this.baseURL = baseURL;
    }

    async analyzeAll(text) {
        const startTime = Date.now();

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
    }

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
}