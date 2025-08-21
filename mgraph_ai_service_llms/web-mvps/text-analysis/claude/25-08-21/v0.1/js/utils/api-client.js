// API Client for Text Analysis Service
export class APIClient {
    constructor(baseURL = '/platform/open-router/text-analysis') {
        this.baseURL = baseURL;
    }
    
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
    
    async analyzeFacts(text) {
        try {
            const response = await fetch(`${this.baseURL}/facts`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });
            return await response.json();
        } catch (error) {
            console.error('Facts API Error:', error);
            return { facts: [], facts_count: 0 };
        }
    }
    
    async analyzeDataPoints(text) {
        try {
            const response = await fetch(`${this.baseURL}/data-points`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });
            return await response.json();
        } catch (error) {
            console.error('Data Points API Error:', error);
            return { data_points: [], data_points_count: 0 };
        }
    }
    
    async generateQuestions(text) {
        try {
            const response = await fetch(`${this.baseURL}/questions`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });
            return await response.json();
        } catch (error) {
            console.error('Questions API Error:', error);
            return { questions: [], questions_count: 0 };
        }
    }
    
    async generateHypotheses(text) {
        try {
            const response = await fetch(`${this.baseURL}/hypotheses`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });
            return await response.json();
        } catch (error) {
            console.error('Hypotheses API Error:', error);
            return { hypotheses: [], hypotheses_count: 0 };
        }
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