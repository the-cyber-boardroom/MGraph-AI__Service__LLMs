import { AnalysisPanel as AnalysisPanelV1 } from '../../../v0.1/js/components/analysis-panel.js';
import { TextFormatter } from '../../../v0.1/js/utils/text-formatter.js';

export class AnalysisPanel extends AnalysisPanelV1 {
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
            <h4>Extracted Facts</h4>
            <ul class="analysis-list">
                ${facts.map(fact => `
                    <li class="analysis-item">${TextFormatter.escapeHtml(fact)}</li>
                `).join('')}
            </ul>
        `;
    }

    updateDataPoints(dataPoints) {
        const section = this.querySelector('#data-points-section');

        if (dataPoints.length === 0) {
            section.innerHTML = '<div class="empty-state">No data points extracted</div>';
            return;
        }

        section.innerHTML = `
            <h4>Data Points</h4>
            <div>
                ${dataPoints.map(point => `
                    <div class="data-point">
                        ${TextFormatter.highlightNumbers(TextFormatter.escapeHtml(point))}
                    </div>
                `).join('')}
            </div>
        `;
    }

    updateQuestions(questions) {
        const section = this.querySelector('#questions-section');

        if (questions.length === 0) {
            section.innerHTML = '<div class="empty-state">No questions generated</div>';
            return;
        }

        section.innerHTML = `
            <h4>Generated Questions</h4>
            <p class="helper-text">💡 Questions to explore about this topic</p>
            <ul class="analysis-list">
                ${questions.map((question, index) => `
                    <li class="analysis-item question-item" data-question="${index}">
                        <div class="question-text">${TextFormatter.escapeHtml(question)}</div>
                        <button class="generate-answer-btn" data-question-index="${index}">Generate Answer</button>
                    </li>
                `).join('')}
            </ul>
        `;

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

                        // Dispatch event with question and answer
                        this.dispatchEvent(new CustomEvent('answer-generated', {
                            detail: {
                                question: question,
                                answer: data.response_text
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
    }

    updateHypotheses(hypotheses) {
        const section = this.querySelector('#hypotheses-section');

        if (hypotheses.length === 0) {
            section.innerHTML = '<div class="empty-state">No hypotheses generated</div>';
            return;
        }

        section.innerHTML = `
            <h4>Hypotheses</h4>
            <div>
                ${hypotheses.map(hypothesis => `
                    <div class="hypothesis-card">
                        ${TextFormatter.escapeHtml(hypothesis)}
                    </div>
                `).join('')}
            </div>
        `;
    }
}