import { AnalysisPanel as AnalysisPanelV3 } from '../../../v0.3/js/components/analysis-panel-v3.js';
import { TextFormatter } from '../../../v0.1/js/utils/text-formatter.js';

export class AnalysisPanel extends AnalysisPanelV3 {

    updateQuestions(questions) {
        const section = this.querySelector('#questions-section');

        if (questions.length === 0) {
            section.innerHTML = '<div class="empty-state">No questions generated</div>';
            return;
        }

        // For local view, add both "Add Question" and "Generate Answer" buttons
        if (!this.isGlobalView) {
            section.innerHTML = `
                <h4>Generated Questions</h4>
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
        } else {
            // Global view - just list questions
            super.updateGlobalQuestions(questions);
        }
    }
}