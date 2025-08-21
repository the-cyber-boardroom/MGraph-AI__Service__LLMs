import { AnalysisPanel as AnalysisPanelV4 } from '../../../v4/js/components/analysis-panel-v4.js';
import { TextFormatter } from '../../../v1/js/utils/text-formatter.js';

export class AnalysisPanel extends AnalysisPanelV4 {
    constructor() {
        super();
        this.currentCacheIds = {};
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
            super.updateGlobalQuestions(questions);
        }
    }

    showGlobalAnalysis(globalData) {
        super.showGlobalAnalysis(globalData);

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
}