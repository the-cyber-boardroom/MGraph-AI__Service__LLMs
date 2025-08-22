// Analysis Panel Component
import { TextFormatter } from '../utils/text-formatter.js';

export class AnalysisPanel extends HTMLElement {
    constructor() {
        super();
        this.currentAnalysis = null;
        this.activeTab = 'summary';
    }
    
    connectedCallback() {
        this.render();
        this.setupEventListeners();
    }
    
    render() {
        this.className = 'analysis-panel';
        this.innerHTML = `
            <div class="analysis-header">
                <h3>Analysis Results</h3>
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
    }
    
    setupEventListeners() {
        // Tab switching
        this.tabs.forEach(tab => {
            tab.addEventListener('click', () => this.switchTab(tab.dataset.tab));
        });
    }
    
    switchTab(tabName) {
        this.activeTab = tabName;
        
        // Update tab states
        this.tabs.forEach(tab => {
            if (tab.dataset.tab === tabName) {
                tab.classList.add('active');
            } else {
                tab.classList.remove('active');
            }
        });
        
        // Update section visibility
        this.sections.forEach(section => {
            if (section.id === `${tabName}-section`) {
                section.classList.add('active');
            } else {
                section.classList.remove('active');
            }
        });
    }
    
    updateAnalysis(analysis) {
        if (!analysis) {
            this.clearAnalysis();
            return;
        }
        
        this.currentAnalysis = analysis;
        
        // Update cache indicator
        this.updateCacheIndicator(analysis);
        
        // Update each section
        this.updateSummary(analysis);
        this.updateFacts(analysis.facts || []);
        this.updateDataPoints(analysis.data_points || []);
        this.updateQuestions(analysis.questions || []);
        this.updateHypotheses(analysis.hypotheses || []);
        
        // Update badges
        this.updateBadges(analysis.summary || {});
        
        // Hide loading
        this.hideLoading();
    }
    
    updateCacheIndicator(analysis) {
        if (analysis.responseTime !== undefined) {
            this.cacheIndicator.style.display = 'inline-block';
            this.cacheIndicator.className = analysis.fromCache 
                ? 'cache-indicator cached' 
                : 'cache-indicator fresh';
            this.cacheIndicator.textContent = 
                `${analysis.fromCache ? 'Cached' : 'Fresh'} • ${TextFormatter.formatResponseTime(analysis.responseTime)}`;
        } else {
            this.cacheIndicator.style.display = 'none';
        }
    }
    
    updateSummary(analysis) {
        const section = this.querySelector('#summary-section');
        const summary = analysis.summary || {};
        
        section.innerHTML = `
            <div class="summary-grid">
                <div class="summary-card">
                    <div class="summary-number">${summary.facts_count || 0}</div>
                    <div class="summary-label">Facts</div>
                </div>
                <div class="summary-card">
                    <div class="summary-number">${summary.data_points_count || 0}</div>
                    <div class="summary-label">Data Points</div>
                </div>
                <div class="summary-card">
                    <div class="summary-number">${summary.questions_count || 0}</div>
                    <div class="summary-label">Questions</div>
                </div>
                <div class="summary-card">
                    <div class="summary-number">${summary.hypotheses_count || 0}</div>
                    <div class="summary-label">Hypotheses</div>
                </div>
            </div>
            ${analysis.model ? `<p style="margin-top: 1rem; color: var(--text-secondary); font-size: 0.875rem;">
                Model: ${analysis.model} • Provider: ${analysis.provider || 'default'}
            </p>` : ''}
        `;
    }
    
    updateFacts(facts) {
        const section = this.querySelector('#facts-section');
        
        if (facts.length === 0) {
            section.innerHTML = '<div class="empty-state">No facts extracted</div>';
            return;
        }
        
        section.innerHTML = `
            <button class="copy-btn" data-section="facts">Copy All</button>
            <h4>Extracted Facts</h4>
            <ul class="analysis-list">
                ${facts.map(fact => `
                    <li class="analysis-item">${TextFormatter.escapeHtml(fact)}</li>
                `).join('')}
            </ul>
        `;
        
        // Add copy handler
        section.querySelector('.copy-btn').addEventListener('click', () => {
            this.copySection('facts', facts);
        });
    }
    
    updateDataPoints(dataPoints) {
        const section = this.querySelector('#data-points-section');
        
        if (dataPoints.length === 0) {
            section.innerHTML = '<div class="empty-state">No data points extracted</div>';
            return;
        }
        
        section.innerHTML = `
            <button class="copy-btn" data-section="data-points">Copy All</button>
            <h4>Data Points</h4>
            <div>
                ${dataPoints.map(point => `
                    <div class="data-point">
                        ${TextFormatter.highlightNumbers(TextFormatter.escapeHtml(point))}
                    </div>
                `).join('')}
            </div>
        `;
        
        // Add copy handler
        section.querySelector('.copy-btn').addEventListener('click', () => {
            this.copySection('data-points', dataPoints);
        });
    }
    
    updateQuestions(questions) {
        const section = this.querySelector('#questions-section');
        
        if (questions.length === 0) {
            section.innerHTML = '<div class="empty-state">No questions generated</div>';
            return;
        }
        
        section.innerHTML = `
            <button class="copy-btn" data-section="questions">Copy All</button>
            <h4>Generated Questions</h4>
            <p class="helper-text">Click any question to add it to the chat</p>
            <ul class="analysis-list">
                ${questions.map((question, index) => `
                    <li class="analysis-item clickable" data-question="${index}">
                        ${TextFormatter.escapeHtml(question)}
                    </li>
                `).join('')}
            </ul>
        `;
        
        // Add click handlers for questions
        section.querySelectorAll('.analysis-item.clickable').forEach((item, index) => {
            item.addEventListener('click', () => {
                this.dispatchEvent(new CustomEvent('question-clicked', {
                    detail: { question: questions[index] },
                    bubbles: true
                }));
            });
        });
        
        // Add copy handler
        section.querySelector('.copy-btn').addEventListener('click', () => {
            this.copySection('questions', questions);
        });
    }
    
    updateHypotheses(hypotheses) {
        const section = this.querySelector('#hypotheses-section');
        
        if (hypotheses.length === 0) {
            section.innerHTML = '<div class="empty-state">No hypotheses generated</div>';
            return;
        }
        
        section.innerHTML = `
            <button class="copy-btn" data-section="hypotheses">Copy All</button>
            <h4>Hypotheses</h4>
            <div>
                ${hypotheses.map(hypothesis => `
                    <div class="hypothesis-card">
                        ${TextFormatter.escapeHtml(hypothesis)}
                    </div>
                `).join('')}
            </div>
        `;
        
        // Add copy handler
        section.querySelector('.copy-btn').addEventListener('click', () => {
            this.copySection('hypotheses', hypotheses);
        });
    }
    
    updateBadges(summary) {
        const badges = {
            'facts': summary.facts_count || 0,
            'data-points': summary.data_points_count || 0,
            'questions': summary.questions_count || 0,
            'hypotheses': summary.hypotheses_count || 0
        };
        
        Object.entries(badges).forEach(([tab, count]) => {
            const tabElement = this.querySelector(`[data-tab="${tab}"] .tab-badge`);
            if (tabElement) {
                tabElement.textContent = count;
            }
        });
    }
    
    copySection(sectionName, items) {
        const content = items.join('\n');
        
        navigator.clipboard.writeText(content).then(() => {
            const btn = this.querySelector(`#${sectionName}-section .copy-btn`);
            if (btn) {
                const originalText = btn.textContent;
                btn.textContent = 'Copied!';
                btn.classList.add('copied');
                
                setTimeout(() => {
                    btn.textContent = originalText;
                    btn.classList.remove('copied');
                }, 2000);
            }
        }).catch(err => {
            console.error('Failed to copy:', err);
        });
    }
    
    showLoading() {
        // Show loading in active section
        const activeSection = this.querySelector('.analysis-section.active');
        if (activeSection && activeSection.id !== 'summary-section') {
            activeSection.innerHTML = '<div class="loading-spinner"></div>';
        }
    }
    
    hideLoading() {
        // Loading will be replaced by content update
    }
    
    clearAnalysis() {
        this.currentAnalysis = null;
        
        // Reset summary
        this.querySelector('#summary-section').innerHTML = `
            <div class="empty-state">
                <p>No analysis yet. Enter some text to get started!</p>
            </div>
        `;
        
        // Clear other sections
        ['facts', 'data-points', 'questions', 'hypotheses'].forEach(section => {
            this.querySelector(`#${section}-section`).innerHTML = '';
        });
        
        // Reset badges
        this.querySelectorAll('.tab-badge').forEach(badge => {
            badge.textContent = '0';
        });
        
        // Hide cache indicator
        this.cacheIndicator.style.display = 'none';
        
        // Reset to summary tab
        this.switchTab('summary');
    }
    
    // Public method to get current analysis
    getCurrentAnalysis() {
        return this.currentAnalysis;
    }
}