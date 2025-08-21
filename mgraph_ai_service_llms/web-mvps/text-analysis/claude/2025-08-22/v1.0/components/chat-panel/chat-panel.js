// mgraph_ai_service_llms/web-mvps/text-analysis/v1.0/components/chat-panel/chat-panel.js

import { TextFormatter } from '../../utils/text-formatter.js';
import { getRandomSample, getRandomWelcome } from '../../utils/sample-texts.js';

export class ChatPanel extends HTMLElement {
    constructor() {
        super();
        this.messages = [];
        this.isFirstLoad = true;
    }

    connectedCallback() {
        this.render();
        this.setupEventListeners();
        this.initialize();
    }

    render() {
        this.className = 'chat-panel';
        this.innerHTML = `
            <div class="chat-header">
                <h2>Text Analysis Chat</h2>
                <button class="btn btn-secondary" id="clearChat">Clear</button>
            </div>
            <div class="chat-messages" id="chatMessages"></div>
            <div class="chat-input-area">
                <div class="chat-input-wrapper">
                    <textarea 
                        class="chat-input" 
                        id="chatInput" 
                        placeholder="Enter text to analyze..."
                    ></textarea>
                    <div class="chat-actions">
                        <button class="btn btn-primary" id="sendBtn">Analyze</button>
                        <button class="btn btn-secondary" id="sampleBtn">Sample</button>
                    </div>
                </div>
                <div class="char-count" id="charCount">0 / 8000 characters</div>
            </div>
        `;

        // Store references to elements
        this.chatInput = this.querySelector('#chatInput');
        this.sendBtn = this.querySelector('#sendBtn');
        this.sampleBtn = this.querySelector('#sampleBtn');
        this.clearBtn = this.querySelector('#clearChat');
        this.chatMessages = this.querySelector('#chatMessages');
        this.charCount = this.querySelector('#charCount');
    }

    setupEventListeners() {
        // Input handling
        this.chatInput.addEventListener('input', () => this.handleInput());
        this.chatInput.addEventListener('keydown', (e) => this.handleKeydown(e));

        // Button clicks
        this.sendBtn.addEventListener('click', () => this.handleSend());
        this.sampleBtn.addEventListener('click', () => this.loadSampleText());
        this.clearBtn.addEventListener('click', () => this.clearChat());
    }

    initialize() {
        // Add welcome message
        this.addMessage(getRandomWelcome(), 'system');

        // Load sample text on first load
        if (this.isFirstLoad) {
            this.loadSampleText();
            this.isFirstLoad = false;
        }
    }

    handleInput() {
        const length = this.chatInput.value.length;
        const validation = TextFormatter.validateTextLength(this.chatInput.value, 10, 8000);

        // Update character count
        this.charCount.textContent = `${length} / 8000 characters`;

        // Update styles based on validation
        if (length > 8000) {
            this.charCount.className = 'char-count error';
            this.sendBtn.disabled = true;
        } else if (length < 10) {
            this.charCount.className = 'char-count';
            this.sendBtn.disabled = true;
        } else {
            this.charCount.className = 'char-count';
            this.sendBtn.disabled = false;
        }
    }

    handleKeydown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            this.handleSend();
        }
    }

    async handleSend() {
        const text = this.chatInput.value.trim();
        const validation = TextFormatter.validateTextLength(text, 10, 8000);

        if (!validation.isValid) {
            this.showError(validation.message);
            return;
        }

        // Add user message
        this.addMessage(text, 'user');

        // Clear input
        this.chatInput.value = '';
        this.handleInput();

        // Show loading
        this.setLoading(true);

        // Emit event for parent to handle
        this.dispatchEvent(new CustomEvent('message-sent', {
            detail: { text },
            bubbles: true
        }));

        // Remove loading state after a delay (parent will handle actual response)
        setTimeout(() => this.setLoading(false), 100);
    }

    // Enhanced addMessage method with cache ID support and question handling
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

    // Add analysis message with cache IDs display
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

    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 50);
    }

    loadSampleText() {
        const sample = getRandomSample();
        this.chatInput.value = sample;
        this.handleInput();
        this.chatInput.focus();
    }

    clearChat() {
        this.messages = [];
        this.chatMessages.innerHTML = '';
        this.addMessage(getRandomWelcome(), 'system');

        // Emit clear event
        this.dispatchEvent(new CustomEvent('chat-cleared', {
            bubbles: true
        }));
    }

    setLoading(loading) {
        if (loading) {
            this.sendBtn.disabled = true;
            this.sendBtn.innerHTML = '<span class="loading-spinner"></span>';
        } else {
            this.sendBtn.disabled = false;
            this.sendBtn.innerHTML = 'Analyze';
            this.handleInput(); // Recheck if button should be enabled
        }
    }

    showError(message) {
        // Temporarily show error in button
        const originalText = this.sendBtn.textContent;
        this.sendBtn.textContent = message;
        this.sendBtn.disabled = true;

        setTimeout(() => {
            this.sendBtn.textContent = originalText;
            this.handleInput();
        }, 2000);
    }

    // Public method to set input text (for question clicks)
    setInputText(text) {
        this.chatInput.value = text;
        this.handleInput();
        this.chatInput.focus();

        // Scroll to input
        this.chatInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    // Public method to get message history
    getMessages() {
        return this.messages;
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