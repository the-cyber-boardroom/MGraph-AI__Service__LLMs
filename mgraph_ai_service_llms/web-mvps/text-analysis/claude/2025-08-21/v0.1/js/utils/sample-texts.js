// Sample texts for demonstration and testing
export const SAMPLE_TEXTS = {
    default: "The company reported Q3 revenue of $5.2 million, a 30% increase year-over-year. CEO Jane Smith announced plans to hire 50 new employees by December. The expansion focuses on the engineering and sales departments, with a particular emphasis on AI and machine learning expertise. Market analysts predict continued growth through Q4, citing strong product adoption and customer retention rates.",
    
    technical: "The new API endpoint processes requests in under 100ms with a 99.9% uptime SLA. It supports both REST and GraphQL protocols, handling up to 10,000 concurrent connections. The system uses Redis for caching with a 15-minute TTL and PostgreSQL for persistent storage. Load balancing is managed through AWS ALB with automatic failover to backup regions.",
    
    product: "Our latest product release includes five major features requested by enterprise customers. Beta testing showed a 40% improvement in user engagement and a 25% reduction in support tickets. The rollout plan targets 1000 users in week one, scaling to full deployment by month end. Key features include advanced analytics, real-time collaboration, and automated workflow management.",
    
    financial: "The quarterly financial report shows total assets of $15.7 million, with liabilities at $3.2 million. Operating expenses decreased by 12% compared to last quarter, while gross profit margin improved to 68%. The company maintains a healthy cash position of $4.5 million with a current ratio of 2.3. Investment in R&D increased by 25% to accelerate product development.",
    
    marketing: "The digital marketing campaign reached 2.5 million impressions with a CTR of 3.2%. Conversion rate improved to 4.8% following A/B testing of landing pages. Social media engagement increased by 145% month-over-month. The campaign generated 8,500 qualified leads with an average CAC of $125. ROI stands at 320% with continued optimization planned for Q4.",
    
    research: "The study analyzed data from 10,000 participants over a 24-month period. Results show a statistically significant correlation (p<0.001) between the intervention and outcome measures. The control group showed 15% improvement while the treatment group achieved 47% improvement. Effect size was large (Cohen's d = 0.85) with 95% confidence intervals ranging from 0.72 to 0.98.",
    
    startup: "The startup secured $3.5 million in Series A funding led by Venture Partners. Current burn rate is $200,000 per month with 18 months of runway. The team has grown from 5 to 23 employees in the past year. Monthly recurring revenue reached $150,000 with 85% month-over-month growth. The platform now serves 500 active customers across 15 countries."
};

// Function to get a random sample
export function getRandomSample() {
    const keys = Object.keys(SAMPLE_TEXTS);
    const randomKey = keys[Math.floor(Math.random() * keys.length)];
    return SAMPLE_TEXTS[randomKey];
}

// Function to get sample by key
export function getSampleByKey(key) {
    return SAMPLE_TEXTS[key] || SAMPLE_TEXTS.default;
}

// Function to get all sample keys
export function getSampleKeys() {
    return Object.keys(SAMPLE_TEXTS);
}

// Welcome messages for chat
export const WELCOME_MESSAGES = [
    "Welcome! Enter some text below to analyze it for facts, data points, questions, and hypotheses.",
    "Hello! I'm ready to analyze your text. Paste or type your content below.",
    "Hi there! Share any text and I'll extract key information and insights for you.",
    "Welcome to Text Analyzer! Click 'Sample' to load example text or enter your own."
];

// Function to get random welcome message
export function getRandomWelcome() {
    return WELCOME_MESSAGES[Math.floor(Math.random() * WELCOME_MESSAGES.length)];
}