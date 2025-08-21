// mgraph_ai_service_llms/web-mvps/text-analysis/v1.0/components/analysis-dashboard/analysis-dashboard.js

export class AnalysisDashboard extends HTMLElement {
    constructor() {
        super();
        this.globalData = null;
        this.analyses = null;
    }

    connectedCallback() {
        this.render();
        this.setupEventListeners();
    }

    render() {
        this.className = 'analysis-dashboard';
        this.innerHTML = `
            <div class="dashboard-container">
                <div class="dashboard-header">
                    <h2>Analysis Dashboard</h2>
                    <div class="dashboard-actions">
                        <button class="generate-summary-btn">Generate Summary</button>
                    </div>
                </div>
                
                <div class="search-section">
                    <input type="text" 
                           class="search-input" 
                           placeholder="Search across all analyses..." 
                           id="searchInput">
                    <button class="search-btn">Search</button>
                </div>
                
                <div class="summary-section" id="summarySection" style="display: none;">
                    <h3>Executive Summary</h3>
                    <div class="summary-content" id="summaryContent"></div>
                </div>
                
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value" id="totalFacts">0</div>
                        <div class="metric-label">Total Facts</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" id="totalDataPoints">0</div>
                        <div class="metric-label">Data Points</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" id="totalQuestions">0</div>
                        <div class="metric-label">Questions</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" id="totalHypotheses">0</div>
                        <div class="metric-label">Hypotheses</div>
                    </div>
                </div>
                
                <div class="search-results" id="searchResults" style="display: none;">
                    <h3>Search Results</h3>
                    <div class="results-list" id="resultsList"></div>
                </div>
                
                <div class="all-items-section">
                    <div class="items-tabs">
                        <button class="item-tab active" data-type="facts">Facts</button>
                        <button class="item-tab" data-type="data_points">Data Points</button>
                        <button class="item-tab" data-type="questions">Questions</button>
                        <button class="item-tab" data-type="hypotheses">Hypotheses</button>
                    </div>
                    <div class="items-content" id="itemsContent">
                        <div class="items-list" id="factsList"></div>
                    </div>
                </div>
            </div>
        `;
    }

    setupEventListeners() {
        // Search functionality
        const searchInput = this.querySelector('#searchInput');
        const searchBtn = this.querySelector('.search-btn');

        searchBtn.addEventListener('click', () => {
            const query = searchInput.value.trim();
            if (query) {
                this.dispatchEvent(new CustomEvent('search-analyses', {
                    detail: { query },
                    bubbles: true
                }));
            }
        });

        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                searchBtn.click();
            }
        });

        // Generate summary button
        this.querySelector('.generate-summary-btn').addEventListener('click', () => {
            this.dispatchEvent(new CustomEvent('generate-summary', {
                bubbles: true
            }));
        });

        // Tab switching
        this.querySelectorAll('.item-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                this.querySelectorAll('.item-tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                this.displayItemsForType(tab.dataset.type);
            });
        });
    }

    updateDashboard(globalData, analyses) {
        this.globalData = globalData;
        this.analyses = analyses;

        // Update metrics
        this.querySelector('#totalFacts').textContent = globalData.summary.facts_count;
        this.querySelector('#totalDataPoints').textContent = globalData.summary.data_points_count;
        this.querySelector('#totalQuestions').textContent = globalData.summary.questions_count;
        this.querySelector('#totalHypotheses').textContent = globalData.summary.hypotheses_count;

        // Display facts by default
        this.displayItemsForType('facts');
    }

    displayItemsForType(type) {
        const itemsContent = this.querySelector('#itemsContent');
        const items = this.globalData ? this.globalData[type] || [] : [];

        if (items.length === 0) {
            itemsContent.innerHTML = '<div class="no-items">No items found</div>';
            return;
        }

        let html = '<div class="items-list">';
        items.forEach((item, index) => {
            html += `
                <div class="dashboard-item">
                    <span class="item-number">${index + 1}.</span>
                    <span class="item-text">${this.escapeHtml(item)}</span>
                </div>
            `;
        });
        html += '</div>';

        itemsContent.innerHTML = html;
    }

    displaySummary(summaryText) {
        const summarySection = this.querySelector('#summarySection');
        const summaryContent = this.querySelector('#summaryContent');

        summaryContent.innerHTML = `
            <div class="generated-summary">
                ${this.escapeHtml(summaryText)}
            </div>
            <div class="summary-timestamp">
                Generated at ${new Date().toLocaleTimeString()}
            </div>
        `;

        summarySection.style.display = 'block';
    }

    displaySearchResults(results, query) {
        const searchResults = this.querySelector('#searchResults');
        const resultsList = this.querySelector('#resultsList');

        if (results.length === 0) {
            resultsList.innerHTML = `<div class="no-results">No results found for "${query}"</div>`;
        } else {
            let html = '';
            results.forEach(result => {
                html += `
                    <div class="search-result-item">
                        <div class="result-header">
                            Analysis #${result.number} - ${new Date(result.timestamp).toLocaleString()}
                        </div>
                        <div class="result-preview">
                            ${this.escapeHtml(result.text.substring(0, 200))}...
                        </div>
                    </div>
                `;
            });
            resultsList.innerHTML = html;
        }

        searchResults.style.display = 'block';
    }

    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;'
        };
        return text.replace(/[&<>"']/g, char => map[char]);
    }
}