// mgraph_ai_service_llms/web-mvps/text-analysis/v1.0/components/analysis-panel/analysis-panel.js

import { TextFormatter } from '../../utils/text-formatter.js';

export class AnalysisPanel extends HTMLElement {
    constructor() {
        super();
        this.currentAnalysis = null;
        this.activeTab = 'summary';
        this.isGlobalView = true;
        this.currentAnalysisId = null;
        this.currentCacheIds = {};
    }

    connectedCallback() {
        this.render();
        this.setupEventListeners();
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

            // Fixed logic: <500ms = cached, 500-2000ms = fresh, >2000ms = slow
            let className, text;
            if (analysis.responseTime < 500) {
                className = 'cache-indicator cached';
                text = 'Cached';
            } else if (analysis.responseTime < 2000) {
                className = 'cache-indicator fresh';
                text = 'Fresh';
            } else {
                className = 'cache-indicator slow';
                text = 'Processing';
            }

            this.cacheIndicator.className = className;
            this.cacheIndicator.textContent =
                `${text} • ${TextFormatter.formatResponseTime(analysis.responseTime)}`;
        } else {
            this.cacheIndicator.style.display = 'none';
        }
    }

    updateSummary(analysis) {
        const section = this.querySelector('#summary-section');
        const summary = analysis.summary || {};

        section.innerHTML = `
            <div class="summary-grid">
                <div class="summary-card clickable" data-target="facts">
                    <div class="summary-number">${summary.facts_count || 0}</div>
                    <div class="summary-label">FACTS</div>
                </div>
                <div class="summary-card clickable" data-target="data-points">
                    <div class="summary-number">${summary.data_points_count || 0}</div>
                    <div class="summary-label">DATA POINTS</div>
                </div>
                <div class="summary-card clickable" data-target="questions">
                    <div class="summary-number">${summary.questions_count || 0}</div>
                    <div class="summary-label">QUESTIONS</div>
                </div>
                <div class="summary-card clickable" data-target="hypotheses">
                    <div class="summary-number">${summary.hypotheses_count || 0}</div>
                    <div class="summary-label">HYPOTHESES</div>
                </div>
            </div>
            ${analysis.model ? `<p style="margin-top: 1rem; color: var(--text-secondary); font-size: 0.875rem;">
                Model: ${analysis.model} • Provider: ${analysis.provider || 'default'}
            </p>` : ''}
        `;

        // Add click handlers to summary cards
        section.querySelectorAll('.summary-card.clickable').forEach(card => {
            card.addEventListener('click', () => {
                const target = card.dataset.target;
                this.switchTab(target);
            });
        });
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

        // For local view, add both "Add Question" and "Generate Answer" buttons
        if (!this.isGlobalView) {
            const cacheInfo = this.currentCacheIds.questions
                ? `<div style="margin-bottom: 1rem; padding: 0.5rem; background: var(--bg-secondary); border-radius: 4px; font-size: 0.75rem;">
                    <span style="color: var(--text-secondary);">Cache ID:</span> 
                    <code style="cursor: pointer; color: var(--color-primary);" onclick="document.querySelector('analysis-panel').inspectCacheId('${this.currentCacheIds.questions}')">
                        ${this.currentCacheIds.questions}
                    </code>
                </div>`
                : '';

            section.innerHTML = `
                <button class="copy-btn" data-section="questions">Copy All</button>
                <h4>Generated Questions</h4>
                ${cacheInfo}
                <p class="helper-text">💡 Click "Add" to use the question, or "Generate" for an answer</p>
                <ul class="analysis-list">
                    ${questions.map((question, index) => `
                        <li class="analysis-item question-item" data-question="${index}">
                            <div class="question-text">${TextFormatter.escapeHtml(question)}</div>
                            <div class="question-actions">
                                <button class="add-question-btn" data-question-index="${index}">Add Question</button>
                                <button class="generate-answer-btn" data-question-index="${index}">Generate Answer</button>
                            </div>
                        </li>
                    `).join('')}
                </ul>
            `;

            // Add copy handler
            section.querySelector('.copy-btn').addEventListener('click', () => {
                this.copySection('questions', questions);
            });

            // Add click handlers for add question buttons
            section.querySelectorAll('.add-question-btn').forEach((btn) => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const index = parseInt(btn.dataset.questionIndex);
                    const question = questions[index];

                    // Visual feedback
                    btn.textContent = 'Added!';
                    btn.disabled = true;

                    // Emit event to add question to chat input
                    this.dispatchEvent(new CustomEvent('question-added', {
                        detail: { question: question },
                        bubbles: true
                    }));

                    setTimeout(() => {
                        btn.textContent = 'Add Question';
                        btn.disabled = false;
                    }, 1500);
                });
            });

            // Add click handlers for generate answer buttons
            section.querySelectorAll('.generate-answer-btn').forEach((btn) => {
                btn.addEventListener('click', async (e) => {
                    e.stopPropagation();
                    const index = parseInt(btn.dataset.questionIndex);
                    const question = questions[index];

                    // Disable button and show loading
                    btn.disabled = true;
                    btn.textContent = 'Generating...';

                    // Get conversation history from parent
                    const textAnalyzer = this.closest('text-analyzer');
                    const chatPanel = textAnalyzer.querySelector('chat-panel');
                    const messages = chatPanel.getMessages();

                    // Build context from recent messages
                    const contextMessages = messages.slice(-5).map(msg =>
                        `${msg.sender === 'user' ? 'User' : 'Assistant'}: ${msg.text}`
                    ).join('\n');

                    const systemPrompt = `You are analyzing text and answering follow-up questions. Here is the recent conversation context:

${contextMessages}

Now answer the following question in one concise paragraph (2-3 sentences maximum). Be specific and directly address the question based on the context provided.`;

                    try {
                        // Call the LLM API with new schema
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

                        if (response.ok) {
                            const data = await response.json();

                            // Dispatch event with question, answer, and cache ID
                            this.dispatchEvent(new CustomEvent('answer-generated', {
                                detail: {
                                    question: question,
                                    answer: data.response_text,
                                    cacheId: data.cache_id
                                },
                                bubbles: true
                            }));
                        } else {
                            throw new Error(`API responded with status ${response.status}`);
                        }
                    } catch (error) {
                        console.error('Failed to generate answer:', error);
                        // Show error feedback
                        btn.textContent = 'Error - Try Again';
                        setTimeout(() => {
                            btn.textContent = 'Generate Answer';
                            btn.disabled = false;
                        }, 2000);
                        return;
                    }

                    // Reset button
                    btn.textContent = 'Generate Answer';
                    btn.disabled = false;
                });
            });
        } else {
            // Global view - just list questions
            this.updateGlobalQuestions(questions);
        }
    }

    updateGlobalQuestions(questions) {
        const section = this.querySelector('#questions-section');

        if (questions.length === 0) {
            section.innerHTML = '<div class="empty-state">No questions generated</div>';
            return;
        }

        // For global view, questions are just listed without generate button
        section.innerHTML = `
            <button class="copy-btn" data-section="questions">Copy All</button>
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

        // Add cache ID summary if available
        if (globalData.allCacheIds && globalData.allCacheIds.length > 0) {
            const summarySection = this.querySelector('#summary-section');
            const cachesSummary = document.createElement('div');
            cachesSummary.innerHTML = `
                <div style="margin-top: 1rem; padding: 1rem; background: var(--bg-secondary); border-radius: 8px;">
                    <h5 style="margin: 0 0 0.5rem 0; color: var(--text-primary); font-size: 0.875rem;">
                        📊 Cache Summary
                    </h5>
                    <p style="font-size: 0.75rem; color: var(--text-secondary); margin: 0;">
                        Total cached requests: ${globalData.allCacheIds.length * 4} 
                        (${globalData.allCacheIds.length} analyses × 4 types)
                    </p>
                    <button 
                        onclick="document.querySelector('text-analyzer').switchView('llm')"
                        style="
                            margin-top: 0.5rem;
                            padding: 0.375rem 0.75rem;
                            background: var(--color-primary);
                            color: white;
                            border: none;
                            border-radius: 4px;
                            cursor: pointer;
                            font-size: 0.75rem;
                        ">
                        View All Cache Entries →
                    </button>
                </div>
            `;
            summarySection.appendChild(cachesSummary);
        }
    }

    showLocalAnalysis(analysisData, totalAnalyses) {
        this.isGlobalView = false;
        this.currentAnalysisId = analysisData.id;
        this.currentCacheIds = analysisData.cacheIds || {};

        // Update title and show view toggle
        this.analysisTitle.textContent = `Analysis #${analysisData.number}`;
        this.viewToggle.style.display = 'flex';
        this.localViewInfo.textContent = `Analysis #${analysisData.number} of ${totalAnalyses}`;

        // Show the regular analysis with cache IDs
        this.updateAnalysis(analysisData.analysis);

        // Add text preview to summary
        this.addTextPreviewToSummary(analysisData.text);

        // Add cache ID display
        this.addCacheIdDisplay();
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

    addCacheIdDisplay() {
        const summarySection = this.querySelector('#summary-section');

        if (Object.keys(this.currentCacheIds).length > 0) {
            const cacheSection = document.createElement('div');
            cacheSection.className = 'cache-ids-section';
            cacheSection.innerHTML = `
                <h5 style="margin: 1rem 0 0.5rem 0; color: var(--text-secondary); font-size: 0.875rem;">
                    🔗 Cache IDs for this Analysis:
                </h5>
                <div class="cache-ids-grid" style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.5rem;">
                    ${this.buildCacheIdCards()}
                </div>
            `;

            summarySection.appendChild(cacheSection);

            // Add click handlers for cache cards
            cacheSection.querySelectorAll('.cache-id-card').forEach(card => {
                card.addEventListener('click', () => {
                    const cacheId = card.dataset.cacheId;
                    this.inspectCacheId(cacheId);
                });
            });
        }
    }

    buildCacheIdCards() {
        const cards = [];

        if (this.currentCacheIds.facts) {
            cards.push(this.createCacheCard('Facts', this.currentCacheIds.facts, '📝'));
        }
        if (this.currentCacheIds.dataPoints) {
            cards.push(this.createCacheCard('Data Points', this.currentCacheIds.dataPoints, '📊'));
        }
        if (this.currentCacheIds.questions) {
            cards.push(this.createCacheCard('Questions', this.currentCacheIds.questions, '❓'));
        }
        if (this.currentCacheIds.hypotheses) {
            cards.push(this.createCacheCard('Hypotheses', this.currentCacheIds.hypotheses, '💡'));
        }

        return cards.join('');
    }

    createCacheCard(type, cacheId, icon) {
        return `
            <div class="cache-id-card" 
                 data-cache-id="${cacheId}"
                 style="
                     padding: 0.5rem;
                     background: var(--bg-secondary);
                     border: 1px solid var(--border-color);
                     border-radius: 4px;
                     cursor: pointer;
                     transition: all 0.2s;
                     display: flex;
                     align-items: center;
                     gap: 0.5rem;
                 "
                 onmouseover="this.style.borderColor='var(--color-primary)'; this.style.transform='translateY(-2px)'"
                 onmouseout="this.style.borderColor='var(--border-color)'; this.style.transform='translateY(0)'">
                <span style="font-size: 1.25rem;">${icon}</span>
                <div style="flex: 1;">
                    <div style="font-size: 0.75rem; color: var(--text-secondary);">${type}</div>
                    <code style="font-size: 0.75rem; font-family: 'Courier New', monospace;">
                        ${cacheId.substring(0, 8)}...
                    </code>
                </div>
                <span style="color: var(--color-primary); font-size: 0.875rem;">🔍</span>
            </div>
        `;
    }

    inspectCacheId(cacheId) {
        // Emit event to inspect cache ID
        this.dispatchEvent(new CustomEvent('inspect-cache', {
            detail: { cacheId },
            bubbles: true
        }));
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