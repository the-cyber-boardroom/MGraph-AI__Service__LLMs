import { APIClient } from '../utils/api-client-v2.js';

export class TextAnalyzer extends HTMLElement {
    constructor() {
        super();
        this.apiClient = new APIClient();
        this.analyses = new Map(); // Store all analyses with unique IDs
        this.globalAnalysis = {
            facts: new Set(),
            data_points: new Set(),
            questions: new Set(),
            hypotheses: new Set()
        };
        this.currentViewId = 'global'; // 'global' or analysis ID
        this.analysisCounter = 0;
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
            this.clearAllAnalyses();
        });

        // Listen for analysis click events from chat
        this.chatPanel.addEventListener('analysis-clicked', (e) => {
            this.showAnalysis(e.detail.analysisId);
        });

        // Listen for view change from analysis panel
        this.analysisPanel.addEventListener('view-change', (e) => {
            if (e.detail.view === 'global') {
                this.showGlobalAnalysis();
            } else {
                this.showAnalysis(e.detail.analysisId);
            }
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

            // Generate unique ID for this analysis
            const analysisId = `analysis-${++this.analysisCounter}`;
            const timestamp = new Date();

            // Store the analysis with metadata
            this.analyses.set(analysisId, {
                id: analysisId,
                text: text,
                timestamp: timestamp,
                analysis: analysis,
                number: this.analysisCounter
            });

            // Update global analysis
            this.updateGlobalAnalysis(analysis);

            // Add analysis summary to chat
            const message = this.formatAnalysisMessage(analysis);
            this.chatPanel.addAnalysisMessage(message, analysisId, this.analysisCounter);

            // Show the new analysis in the panel
            if (this.currentViewId === 'global') {
                this.showGlobalAnalysis();
            } else {
                this.showAnalysis(analysisId);
            }

        } catch (error) {
            console.error('Analysis error:', error);
            this.chatPanel.addMessage(
                'Sorry, there was an error analyzing the text. Please try again.',
                'system'
            );
            this.analysisPanel.hideLoading();
        }
    }

    updateGlobalAnalysis(analysis) {
        // Add new items to global sets (automatically deduplicates)
        if (analysis.facts) {
            analysis.facts.forEach(fact => this.globalAnalysis.facts.add(fact));
        }
        if (analysis.data_points) {
            analysis.data_points.forEach(dp => this.globalAnalysis.data_points.add(dp));
        }
        if (analysis.questions) {
            analysis.questions.forEach(q => this.globalAnalysis.questions.add(q));
        }
        if (analysis.hypotheses) {
            analysis.hypotheses.forEach(h => this.globalAnalysis.hypotheses.add(h));
        }
    }

    showAnalysis(analysisId) {
        const analysisData = this.analyses.get(analysisId);
        if (analysisData) {
            this.currentViewId = analysisId;
            this.analysisPanel.showLocalAnalysis(analysisData, this.analyses.size);
        }
    }

    showGlobalAnalysis() {
        this.currentViewId = 'global';

        // Convert sets to arrays and create summary
        const globalData = {
            facts: Array.from(this.globalAnalysis.facts),
            data_points: Array.from(this.globalAnalysis.data_points),
            questions: Array.from(this.globalAnalysis.questions),
            hypotheses: Array.from(this.globalAnalysis.hypotheses),
            summary: {
                facts_count: this.globalAnalysis.facts.size,
                data_points_count: this.globalAnalysis.data_points.size,
                questions_count: this.globalAnalysis.questions.size,
                hypotheses_count: this.globalAnalysis.hypotheses.size
            },
            totalAnalyses: this.analyses.size
        };

        this.analysisPanel.showGlobalAnalysis(globalData);
    }

    clearAllAnalyses() {
        this.analyses.clear();
        this.globalAnalysis = {
            facts: new Set(),
            data_points: new Set(),
            questions: new Set(),
            hypotheses: new Set()
        };
        this.analysisCounter = 0;
        this.currentViewId = 'global';
        this.analysisPanel.clearAnalysis();
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
}