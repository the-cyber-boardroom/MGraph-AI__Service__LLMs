import { APIClient } from '../utils/api-client-v2.js';

export class TextAnalyzer extends HTMLElement {
    constructor() {
        super();
        this.apiClient = new APIClient();
        this.currentAnalysis = null;
    }

    connectedCallback() {
        this.render();
        this.setupEventListeners();
    }

    render() {
        this.innerHTML = `
            <div class="text-analyzer-container">
                <chat-panel></chat-panel>
                <analysis-panel></analysis-panel>
            </div>
        `;

        this.chatPanel = this.querySelector('chat-panel');
        this.analysisPanel = this.querySelector('analysis-panel');
    }

    setupEventListeners() {
        // Listen for message from chat panel
        this.chatPanel.addEventListener('message-sent', async (e) => {
            await this.handleAnalyzeText(e.detail.text);
        });

        // Listen for answer generation from analysis panel
        this.analysisPanel.addEventListener('answer-generated', (e) => {
            // Add question and answer to chat
            this.chatPanel.addMessage(e.detail.question, 'user');
            this.chatPanel.addMessage(e.detail.answer, 'system');

            // Analyze the answer
            this.handleAnalyzeText(e.detail.answer);
        });

        // Listen for clear event from chat
        this.chatPanel.addEventListener('chat-cleared', () => {
            this.currentAnalysis = null;
            this.analysisPanel.clearAnalysis();
        });
    }

    async handleAnalyzeText(text) {
        if (!text || text.trim().length < 10) {
            this.chatPanel.addMessage('Please enter at least 10 characters to analyze.', 'system');
            return;
        }

        // Show loading state
        this.analysisPanel.showLoading();

        try {
            // Call API
            const analysis = await this.apiClient.analyzeAll(text);
            this.currentAnalysis = analysis;

            // Update analysis panel
            this.analysisPanel.updateAnalysis(analysis);

            // Add success message to chat
            const message = this.formatAnalysisMessage(analysis);
            this.chatPanel.addMessage(message, 'system');

        } catch (error) {
            console.error('Analysis error:', error);
            this.chatPanel.addMessage(
                'Sorry, there was an error analyzing the text. Please try again.',
                'system'
            );
            this.analysisPanel.hideLoading();
        }
    }

    formatAnalysisMessage(analysis) {
        const parts = [];

        if (analysis.summary.facts_count > 0) {
            parts.push(`${analysis.summary.facts_count} facts`);
        }
        if (analysis.summary.data_points_count > 0) {
            parts.push(`${analysis.summary.data_points_count} data points`);
        }
        if (analysis.summary.questions_count > 0) {
            parts.push(`${analysis.summary.questions_count} questions`);
        }
        if (analysis.summary.hypotheses_count > 0) {
            parts.push(`${analysis.summary.hypotheses_count} hypotheses`);
        }

        if (parts.length === 0) {
            return 'Analysis complete, but no specific information could be extracted.';
        }

        return `Analysis complete! Found ${this.formatList(parts)}.`;
    }

    formatList(items) {
        if (items.length === 0) return '';
        if (items.length === 1) return items[0];
        if (items.length === 2) return items.join(' and ');
        return items.slice(0, -1).join(', ') + ', and ' + items[items.length - 1];
    }

    // Public method to get current analysis
    getCurrentAnalysis() {
        return this.currentAnalysis;
    }

    // Public method to trigger analysis programmatically
    async analyzeText(text) {
        await this.handleAnalyzeText(text);
    }
}