import { AnalysisPanel as AnalysisPanelV2 } from '../../../v2/js/components/analysis-panel-v2.js';
import { TextFormatter } from '../../../v1/js/utils/text-formatter.js';

export class AnalysisPanel extends AnalysisPanelV2 {
    constructor() {
        super();
        this.isGlobalView = true;
        this.currentAnalysisId = null;
    }

    render() {
        this.className = 'analysis-panel';
        this.innerHTML = `
            <div class="analysis-header">
                <div class="analysis-header-content">
                    <h3 id="analysis-title">Analysis Results</h3>
                    <div class="view-toggle" id="viewToggle" style="display: none;">
                        <button class="view-btn" id="globalViewBtn">Global View</button>
                        <span class="view-separator">|</span>
                        <span id="localViewInfo">Analysis #1</span>
                    </div>
                </div>
                <span class="cache-indicator" id="cacheIndicator" style="display: none;"></span>
            </div>
            <div class="analysis-tabs">
                <div class="tab active" data-tab="summary">
                    Summary
                </div>
                <div class="tab" data-tab="facts">
                    Facts <span class="tab-badge">0</span>
                </div>
                <div class="tab" data-tab="data-points">
                    Data Points <span class="tab-badge">0</span>
                </div>
                <div class="tab" data-tab="questions">
                    Questions <span class="tab-badge">0</span>
                </div>
                <div class="tab" data-tab="hypotheses">
                    Hypotheses <span class="tab-badge">0</span>
                </div>
            </div>
            <div class="analysis-content">
                <div class="analysis-section active" id="summary-section">
                    <div class="empty-state">
                        <p>No analysis yet. Enter some text to get started!</p>
                    </div>
                </div>
                <div class="analysis-section" id="facts-section"></div>
                <div class="analysis-section" id="data-points-section"></div>
                <div class="analysis-section" id="questions-section"></div>
                <div class="analysis-section" id="hypotheses-section"></div>
            </div>
        `;

        this.cacheIndicator = this.querySelector('#cacheIndicator');
        this.tabs = this.querySelectorAll('.tab');
        this.sections = this.querySelectorAll('.analysis-section');
        this.viewToggle = this.querySelector('#viewToggle');
        this.globalViewBtn = this.querySelector('#globalViewBtn');
        this.localViewInfo = this.querySelector('#localViewInfo');
        this.analysisTitle = this.querySelector('#analysis-title');

        // Add event listener for global view button
        this.globalViewBtn?.addEventListener('click', () => {
            this.dispatchEvent(new CustomEvent('view-change', {
                detail: { view: 'global' },
                bubbles: true
            }));
        });
    }

    showGlobalAnalysis(globalData) {
        this.isGlobalView = true;
        this.currentAnalysisId = null;

        // Update title and hide view toggle
        this.analysisTitle.textContent = `Global Analysis (${globalData.totalAnalyses} analyses)`;
        this.viewToggle.style.display = 'none';
        this.cacheIndicator.style.display = 'none';

        // Update all sections with global data
        this.updateGlobalSummary(globalData);
        this.updateFacts(globalData.facts || []);
        this.updateDataPoints(globalData.data_points || []);
        this.updateGlobalQuestions(globalData.questions || []);
        this.updateHypotheses(globalData.hypotheses || []);

        // Update badges
        this.updateBadges(globalData.summary || {});

        // Switch to summary tab
        this.switchTab('summary');
    }

    showLocalAnalysis(analysisData, totalAnalyses) {
        this.isGlobalView = false;
        this.currentAnalysisId = analysisData.id;

        // Update title and show view toggle
        this.analysisTitle.textContent = `Analysis #${analysisData.number}`;
        this.viewToggle.style.display = 'flex';
        this.localViewInfo.textContent = `Analysis #${analysisData.number} of ${totalAnalyses}`;

        // Show the regular analysis
        this.updateAnalysis(analysisData.analysis);

        // Add text preview to summary
        this.addTextPreviewToSummary(analysisData.text);
    }

    updateGlobalSummary(globalData) {
        const section = this.querySelector('#summary-section');
        const summary = globalData.summary || {};

        section.innerHTML = `
            <div class="global-summary-header">
                <h4>📊 Combined Analysis from ${globalData.totalAnalyses} text${globalData.totalAnalyses !== 1 ? 's' : ''}</h4>
            </div>
            <div class="summary-grid">
                <div class="summary-card clickable" data-target="facts">
                    <div class="summary-number">${summary.facts_count || 0}</div>
                    <div class="summary-label">TOTAL FACTS</div>
                </div>
                <div class="summary-card clickable" data-target="data-points">
                    <div class="summary-number">${summary.data_points_count || 0}</div>
                    <div class="summary-label">TOTAL DATA POINTS</div>
                </div>
                <div class="summary-card clickable" data-target="questions">
                    <div class="summary-number">${summary.questions_count || 0}</div>
                    <div class="summary-label">TOTAL QUESTIONS</div>
                </div>
                <div class="summary-card clickable" data-target="hypotheses">
                    <div class="summary-number">${summary.hypotheses_count || 0}</div>
                    <div class="summary-label">TOTAL HYPOTHESES</div>
                </div>
            </div>
            <p style="margin-top: 1rem; color: var(--text-secondary); font-size: 0.875rem; text-align: center;">
                Unique items collected across all analyses (duplicates removed)
            </p>
        `;

        // Add click handlers to summary cards
        section.querySelectorAll('.summary-card.clickable').forEach(card => {
            card.addEventListener('click', () => {
                const target = card.dataset.target;
                this.switchTab(target);
            });
        });
    }

    updateGlobalQuestions(questions) {
        const section = this.querySelector('#questions-section');

        if (questions.length === 0) {
            section.innerHTML = '<div class="empty-state">No questions generated</div>';
            return;
        }

        // For global view, questions are just listed without generate button
        section.innerHTML = `
            <h4>All Generated Questions</h4>
            <p class="helper-text">📚 Questions collected from all analyses</p>
            <ul class="analysis-list">
                ${questions.map((question) => `
                    <li class="analysis-item">
                        ${TextFormatter.escapeHtml(question)}
                    </li>
                `).join('')}
            </ul>
        `;
    }

    addTextPreviewToSummary(text) {
        const summarySection = this.querySelector('#summary-section');
        const existingContent = summarySection.innerHTML;

        // Add text preview at the top of summary
        const textPreview = `
            <div class="text-preview">
                <h5>Analyzed Text:</h5>
                <p>${TextFormatter.truncate(TextFormatter.escapeHtml(text), 200)}</p>
            </div>
            <hr style="margin: 1rem 0; border: none; border-top: 1px solid var(--border-color);">
        `;

        // Insert preview before the summary grid
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = textPreview + existingContent;
        summarySection.innerHTML = tempDiv.innerHTML;

        // Re-attach click handlers for summary cards
        summarySection.querySelectorAll('.summary-card.clickable').forEach(card => {
            card.addEventListener('click', () => {
                const target = card.dataset.target;
                this.switchTab(target);
            });
        });
    }
}