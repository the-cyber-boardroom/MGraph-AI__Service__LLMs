import { APIClient } from '../utils/api-client-v4.js';

export class TextAnalyzer extends HTMLElement {
    constructor() {
        super();
        this.apiClient = new APIClient();
        this.analyses = new Map();
        this.globalAnalysis = {
            facts: new Set(),
            data_points: new Set(),
            questions: new Set(),
            hypotheses: new Set()
        };
        this.currentViewId = 'global';
        this.analysisCounter = 0;
        this.currentView = 'chat'; // 'chat' or 'analysis'
    }

    connectedCallback() {
        this.render();
        this.setupEventListeners();
        this.setupViewToggle();
    }

    render() {
        this.innerHTML = `
            <div class="view-header">
                <a href="/web-mvps/index.html" class="back-link">← Back to Versions</a>
                <div class="view-toggle-container">
                    <button class="view-toggle-btn active" data-view="chat">Chat View</button>
                    <button class="view-toggle-btn" data-view="analysis">Analysis View</button>
                </div>
            </div>
            <div class="text-analyzer-container" id="chatView">
                <chat-panel></chat-panel>
                <analysis-panel></analysis-panel>
                <activity-log></activity-log>
            </div>
            <div class="text-analyzer-container hidden" id="analysisView">
                <analysis-dashboard></analysis-dashboard>
                <activity-log></activity-log>
            </div>
        `;

        this.chatPanel = this.querySelector('chat-panel');
        this.analysisPanel = this.querySelector('analysis-panel');
        this.activityLog = this.querySelector('activity-log');
        this.analysisDashboard = this.querySelector('analysis-dashboard');
    }

    setupViewToggle() {
        const toggleButtons = this.querySelectorAll('.view-toggle-btn');
        toggleButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const view = btn.dataset.view;
                this.switchView(view);

                // Update button states
                toggleButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            });
        });
    }

    switchView(view) {
        this.currentView = view;
        const chatView = this.querySelector('#chatView');
        const analysisView = this.querySelector('#analysisView');

        if (view === 'chat') {
            chatView.classList.remove('hidden');
            analysisView.classList.add('hidden');
        } else {
            chatView.classList.add('hidden');
            analysisView.classList.remove('hidden');
            // Update analysis dashboard when switching
            this.updateAnalysisDashboard();
        }
    }

    setupEventListeners() {
        // Listen for message from chat panel
        this.chatPanel.addEventListener('message-sent', async (e) => {
            await this.handleAnalyzeText(e.detail.text);
        });

        // Listen for answer generation from analysis panel
        this.analysisPanel.addEventListener('answer-generated', (e) => {
            this.chatPanel.addMessage(e.detail.question, 'user');
            this.chatPanel.addMessage(e.detail.answer, 'system');
            this.handleAnalyzeText(e.detail.answer);
        });

        // Listen for question addition from analysis panel
        this.analysisPanel.addEventListener('question-added', (e) => {
            this.chatPanel.setInputText(e.detail.question);
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

        // Listen for search from analysis dashboard
        this.analysisDashboard?.addEventListener('search-analyses', (e) => {
            this.searchAnalyses(e.detail.query);
        });

        // Listen for summary generation request
        this.analysisDashboard?.addEventListener('generate-summary', async () => {
            await this.generateGlobalSummary();
        });
    }

    async handleAnalyzeText(text) {
        if (!text || text.trim().length < 10) {
            this.chatPanel.addMessage('Please enter at least 10 characters to analyze.', 'system');
            return;
        }

        const analysisId = `analysis-${++this.analysisCounter}`;
        const timestamp = new Date();

        // Log activity
        this.activityLog.addActivity('Starting analysis...', 'info');

        try {
            // Perform parallel API calls for better performance
            this.activityLog.addActivity('Calling APIs in parallel...', 'info');

            const [facts, dataPoints, questions, hypotheses] = await Promise.all([
                this.apiClient.analyzeFacts(text).catch(err => {
                    this.activityLog.addActivity('Facts extraction failed', 'error');
                    return { facts: [], facts_count: 0 };
                }),
                this.apiClient.analyzeDataPoints(text).catch(err => {
                    this.activityLog.addActivity('Data points extraction failed', 'error');
                    return { data_points: [], data_points_count: 0 };
                }),
                this.apiClient.analyzeQuestions(text).catch(err => {
                    this.activityLog.addActivity('Questions generation failed', 'error');
                    return { questions: [], questions_count: 0 };
                }),
                this.apiClient.analyzeHypotheses(text).catch(err => {
                    this.activityLog.addActivity('Hypotheses generation failed', 'error');
                    return { hypotheses: [], hypotheses_count: 0 };
                })
            ]);

            this.activityLog.addActivity('All API calls completed', 'success');

            // Combine results
            const analysis = {
                text: text,
                facts: facts.facts || [],
                data_points: dataPoints.data_points || [],
                questions: questions.questions || [],
                hypotheses: hypotheses.hypotheses || [],
                summary: {
                    facts_count: facts.facts_count || 0,
                    data_points_count: dataPoints.data_points_count || 0,
                    questions_count: questions.questions_count || 0,
                    hypotheses_count: hypotheses.hypotheses_count || 0
                },
                model: facts.model || 'openai/gpt-oss-120b',
                provider: facts.provider || 'groq'
            };

            // Store the analysis
            this.analyses.set(analysisId, {
                id: analysisId,
                text: text,
                timestamp: timestamp,
                analysis: analysis,
                number: this.analysisCounter
            });

            // Update global analysis with deduplication
            await this.updateGlobalAnalysisWithDedup(analysis);

            // Add analysis summary to chat
            const message = this.formatAnalysisMessage(analysis);
            this.chatPanel.addAnalysisMessage(message, analysisId, this.analysisCounter);

            // Show the new analysis
            if (this.currentViewId === 'global') {
                this.showGlobalAnalysis();
            } else {
                this.showAnalysis(analysisId);
            }

            this.activityLog.addActivity('Analysis complete!', 'success');

        } catch (error) {
            console.error('Analysis error:', error);
            this.activityLog.addActivity(`Error: ${error.message}`, 'error');
            this.chatPanel.addMessage('Sorry, there was an error analyzing the text.', 'system');
        }
    }

    async updateGlobalAnalysisWithDedup(analysis) {
        // Use smart deduplication for facts
        if (analysis.facts && analysis.facts.length > 0) {
            this.activityLog.addActivity('Deduplicating facts...', 'info');
            const dedupedFacts = await this.smartDeduplicate(
                Array.from(this.globalAnalysis.facts),
                analysis.facts
            );
            this.globalAnalysis.facts = new Set(dedupedFacts);
        }

        // Simple deduplication for others (exact match)
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

    async smartDeduplicate(existing, newItems) {
        if (existing.length === 0) return newItems;

        try {
            const response = await this.apiClient.deduplicateItems(existing, newItems);
            return response.unique_items || [...existing, ...newItems];
        } catch (error) {
            // Fallback to simple deduplication
            this.activityLog.addActivity('Smart dedup failed, using simple dedup', 'warning');
            return [...new Set([...existing, ...newItems])];
        }
    }

    async generateGlobalSummary() {
        this.activityLog.addActivity('Generating global summary...', 'info');

        const globalData = {
            facts: Array.from(this.globalAnalysis.facts),
            data_points: Array.from(this.globalAnalysis.data_points),
            questions: Array.from(this.globalAnalysis.questions),
            hypotheses: Array.from(this.globalAnalysis.hypotheses)
        };

        try {
            const summary = await this.apiClient.generateSummary(globalData);
            this.analysisDashboard.displaySummary(summary.summary_text);
            this.activityLog.addActivity('Summary generated successfully', 'success');
        } catch (error) {
            this.activityLog.addActivity('Summary generation failed', 'error');
        }
    }

    searchAnalyses(query) {
        const results = [];
        const searchTerm = query.toLowerCase();

        // Search through all analyses
        for (const [id, data] of this.analyses) {
            const analysis = data.analysis;
            let found = false;

            // Search in facts
            if (analysis.facts.some(f => f.toLowerCase().includes(searchTerm))) found = true;
            // Search in data points
            if (analysis.data_points.some(d => d.toLowerCase().includes(searchTerm))) found = true;
            // Search in questions
            if (analysis.questions.some(q => q.toLowerCase().includes(searchTerm))) found = true;
            // Search in hypotheses
            if (analysis.hypotheses.some(h => h.toLowerCase().includes(searchTerm))) found = true;

            if (found) {
                results.push(data);
            }
        }

        this.analysisDashboard.displaySearchResults(results, query);
    }

    updateAnalysisDashboard() {
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

        this.analysisDashboard?.updateDashboard(globalData, this.analyses);
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
        this.activityLog.clear();
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