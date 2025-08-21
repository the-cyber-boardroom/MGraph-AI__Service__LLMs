import { ChatPanel as ChatPanelV4 } from '../../../v4/js/components/chat-panel-v4.js';
import { TextFormatter } from '../../../v1/js/utils/text-formatter.js';

export class ChatPanel extends ChatPanelV4 {

    // Override to add cache ID display in analysis messages
    addAnalysisMessage(text, analysisId, analysisNumber, cacheIds = {}) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message analysis-info';
        messageDiv.dataset.analysisId = analysisId;
        messageDiv.dataset.cacheIds = JSON.stringify(cacheIds);

        const bubble = document.createElement('div');
        bubble.className = 'message-bubble analysis-bubble clickable';

        // Build cache links HTML with better formatting
        const cacheLinksHtml = this.buildCacheLinks(cacheIds);

        bubble.innerHTML = `
            <div class="analysis-main-content">
                <span class="analysis-icon">📊</span>
                <span class="analysis-text">Analysis #${analysisNumber}: ${text}</span>
                <span class="analysis-click-hint">Click to view details →</span>
            </div>
            ${cacheLinksHtml ? `<div class="cache-links-section">${cacheLinksHtml}</div>` : ''}
        `;

        const time = document.createElement('div');
        time.className = 'message-time';
        time.textContent = TextFormatter.formatTimestamp(new Date());

        messageDiv.appendChild(bubble);
        messageDiv.appendChild(time);

        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();

        // Store message with type and cache info
        this.messages.push({
            text,
            sender: 'analysis',
            analysisId: analysisId,
            analysisNumber: analysisNumber,
            cacheIds: cacheIds,
            time: new Date()
        });

        // Add click handler for main bubble
        bubble.addEventListener('click', (e) => {
            // Don't trigger if clicking on cache links
            if (e.target.closest('.cache-link')) {
                return;
            }

            // Visual feedback
            bubble.classList.add('clicked');
            setTimeout(() => bubble.classList.remove('clicked'), 200);

            // Emit event to show this analysis
            this.dispatchEvent(new CustomEvent('analysis-clicked', {
                detail: { analysisId: analysisId },
                bubbles: true
            }));
        });

        // Add handlers for cache links
        bubble.querySelectorAll('.cache-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.stopPropagation();
                e.preventDefault();
                const cacheId = link.dataset.cacheId;

                this.dispatchEvent(new CustomEvent('inspect-cache', {
                    detail: { cacheId: cacheId },
                    bubbles: true
                }));
            });
        });
    }

    buildCacheLinks(cacheIds) {
        if (!cacheIds || Object.keys(cacheIds).length === 0) {
            return '';
        }

        const links = [];

        if (cacheIds.facts) {
            links.push(`
                <a href="#" class="cache-link" data-cache-id="${cacheIds.facts}" title="Facts Cache">
                    <span class="cache-icon">📝</span>
                    <span class="cache-id-text">${cacheIds.facts.substring(0, 6)}...</span>
                </a>
            `);
        }
        if (cacheIds.dataPoints) {
            links.push(`
                <a href="#" class="cache-link" data-cache-id="${cacheIds.dataPoints}" title="Data Points Cache">
                    <span class="cache-icon">📊</span>
                    <span class="cache-id-text">${cacheIds.dataPoints.substring(0, 6)}...</span>
                </a>
            `);
        }
        if (cacheIds.questions) {
            links.push(`
                <a href="#" class="cache-link" data-cache-id="${cacheIds.questions}" title="Questions Cache">
                    <span class="cache-icon">❓</span>
                    <span class="cache-id-text">${cacheIds.questions.substring(0, 6)}...</span>
                </a>
            `);
        }
        if (cacheIds.hypotheses) {
            links.push(`
                <a href="#" class="cache-link" data-cache-id="${cacheIds.hypotheses}" title="Hypotheses Cache">
                    <span class="cache-icon">💡</span>
                    <span class="cache-id-text">${cacheIds.hypotheses.substring(0, 6)}...</span>
                </a>
            `);
        }

        return links.length > 0 ? `
            <div class="cache-links-header">Cache IDs:</div>
            <div class="cache-links-grid">${links.join('')}</div>
        ` : '';
    }

    // Rest of the methods remain the same...
    addMessage(text, sender = 'user', cacheId = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;

        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';

        // Check if this is a question from the user
        const isQuestion = sender === 'user' && text.endsWith('?');

        if (sender === 'system') {
            bubble.innerHTML = `<span class="message-text">${text}</span>`;

            // Add cache link if available
            if (cacheId) {
                bubble.innerHTML += `
                    <div class="message-cache-info">
                        <span class="cache-indicator">🔗</span>
                        <a href="#" class="cache-link-inline" data-cache-id="${cacheId}">
                            Cache: ${cacheId.substring(0, 8)}...
                        </a>
                    </div>
                `;
            }
        } else if (isQuestion) {
            // Add generate answer option for questions
            bubble.innerHTML = `
                <span class="message-text">${text}</span>
                <button class="inline-generate-btn" data-question="${text}">Generate Answer</button>
            `;
        } else {
            bubble.textContent = text;
        }

        const time = document.createElement('div');
        time.className = 'message-time';
        time.textContent = TextFormatter.formatTimestamp(new Date());

        messageDiv.appendChild(bubble);
        messageDiv.appendChild(time);

        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();

        // Store message with cache info
        this.messages.push({
            text,
            sender,
            cacheId,
            time: new Date()
        });

        // Add handler for cache link
        const cacheLink = bubble.querySelector('.cache-link-inline');
        if (cacheLink) {
            cacheLink.addEventListener('click', (e) => {
                e.preventDefault();
                const cacheId = cacheLink.dataset.cacheId;

                this.dispatchEvent(new CustomEvent('inspect-cache', {
                    detail: { cacheId: cacheId },
                    bubbles: true
                }));
            });
        }

        // Add handler for generate answer button if present
        if (isQuestion) {
            const generateBtn = bubble.querySelector('.inline-generate-btn');
            generateBtn?.addEventListener('click', async () => {
                generateBtn.disabled = true;
                generateBtn.textContent = 'Generating...';

                // Get conversation history
                const contextMessages = this.messages.slice(-5).map(msg =>
                    `${msg.sender === 'user' ? 'User' : 'Assistant'}: ${msg.text}`
                ).join('\n');

                const systemPrompt = `You are analyzing text and answering follow-up questions. Here is the recent conversation context:

${contextMessages}

Now answer the following question in one concise paragraph (2-3 sentences maximum). Be specific and directly address the question based on the context provided.`;

                try {
                    const response = await fetch('/platform/open-router/llm-simple/complete', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Accept': 'application/json'
                        },
                        body: JSON.stringify({
                            user_prompt: text,
                            system_prompt: systemPrompt,
                            model: 'gpt-oss-120b',
                            provider: 'groq'
                        })
                    });

                    if (response.ok) {
                        const data = await response.json();

                        // Add response with cache ID if available
                        this.addMessage(data.response_text, 'system', data.cache_id);

                        // Trigger analysis of the answer
                        this.dispatchEvent(new CustomEvent('message-sent', {
                            detail: { text: data.response_text },
                            bubbles: true
                        }));
                    }
                } catch (error) {
                    console.error('Failed to generate answer:', error);
                } finally {
                    generateBtn.remove(); // Remove button after use
                }
            });
        }
    }

    // Method to get all cache IDs from current conversation
    getAllCacheIds() {
        const cacheIds = [];

        this.messages.forEach(msg => {
            if (msg.cacheId) {
                cacheIds.push({
                    type: 'message',
                    cacheId: msg.cacheId,
                    text: msg.text.substring(0, 50) + '...',
                    timestamp: msg.time
                });
            }

            if (msg.cacheIds) {
                Object.entries(msg.cacheIds).forEach(([type, id]) => {
                    if (id) {
                        cacheIds.push({
                            type: type,
                            cacheId: id,
                            text: `Analysis ${msg.analysisNumber} - ${type}`,
                            timestamp: msg.time
                        });
                    }
                });
            }
        });

        return cacheIds;
    }
}