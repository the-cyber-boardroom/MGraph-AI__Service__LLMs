export class LLMRequestViewer extends HTMLElement {
    constructor() {
        super();
        this.currentCacheId = null;
        this.cacheHistory = [];
        this.viewMode = 'single'; // 'single' or 'list'
    }

    connectedCallback() {
        this.render();
        this.setupEventListeners();

        // Listen for cache ID captures
        window.addEventListener('cache-id-captured', (e) => {
            this.addToHistory(e.detail);
        });
    }

    render() {
        this.className = 'llm-request-viewer';
        this.innerHTML = `
            <div class="viewer-container">
                <div class="viewer-header">
                    <h2>LLM Request Inspector</h2>
                    <div class="view-controls">
                        <button class="view-mode-btn active" data-mode="single">Single View</button>
                        <button class="view-mode-btn" data-mode="list">List View</button>
                        <button class="refresh-btn" id="refreshStats">🔄 Refresh Stats</button>
                    </div>
                </div>
                
                <div class="cache-stats" id="cacheStats">
                    <div class="stat-card">
                        <div class="stat-value">-</div>
                        <div class="stat-label">Total Cached</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">-</div>
                        <div class="stat-label">Cache Hits Today</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">-</div>
                        <div class="stat-label">Cost Saved</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">-</div>
                        <div class="stat-label">Avg Response Time</div>
                    </div>
                </div>
                
                <div class="viewer-content">
                    <!-- Single View Mode -->
                    <div class="single-view" id="singleView">
                        <div class="cache-id-input">
                            <input type="text" 
                                   id="cacheIdInput" 
                                   placeholder="Enter Cache ID or select from history..."
                                   class="cache-input">
                            <button class="inspect-btn" id="inspectBtn">🔍 Inspect</button>
                        </div>
                        
                        <div class="request-response-viewer" id="requestResponseViewer">
                            <div class="empty-state">
                                Enter a Cache ID to inspect the request/response pair
                            </div>
                        </div>
                    </div>
                    
                    <!-- List View Mode -->
                    <div class="list-view hidden" id="listView">
                        <div class="history-filters">
                            <select id="typeFilter">
                                <option value="all">All Types</option>
                                <option value="facts">Facts</option>
                                <option value="dataPoints">Data Points</option>
                                <option value="questions">Questions</option>
                                <option value="hypotheses">Hypotheses</option>
                                <option value="answer">Answers</option>
                                <option value="summary">Summaries</option>
                            </select>
                            <button class="clear-history-btn" id="clearHistory">Clear History</button>
                        </div>
                        
                        <div class="cache-history" id="cacheHistoryList">
                            <div class="empty-state">
                                No cache entries captured yet. Start analyzing text to see requests here.
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    setupEventListeners() {
        // View mode switching
        this.querySelectorAll('.view-mode-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.switchViewMode(btn.dataset.mode);
            });
        });

        // Inspect button
        this.querySelector('#inspectBtn').addEventListener('click', () => {
            const cacheId = this.querySelector('#cacheIdInput').value.trim();
            if (cacheId) {
                this.inspectCacheEntry(cacheId);
            }
        });

        // Enter key in input
        this.querySelector('#cacheIdInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.querySelector('#inspectBtn').click();
            }
        });

        // Refresh stats
        this.querySelector('#refreshStats').addEventListener('click', () => {
            this.loadCacheStats();
        });

        // Type filter
        this.querySelector('#typeFilter').addEventListener('change', (e) => {
            this.filterHistory(e.target.value);
        });

        // Clear history
        this.querySelector('#clearHistory').addEventListener('click', () => {
            this.cacheHistory = [];
            this.updateHistoryDisplay();
        });

        // Load initial stats
        this.loadCacheStats();
    }

    switchViewMode(mode) {
        this.viewMode = mode;

        // Update button states
        this.querySelectorAll('.view-mode-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.mode === mode);
        });

        // Toggle views
        const singleView = this.querySelector('#singleView');
        const listView = this.querySelector('#listView');

        if (mode === 'single') {
            singleView.classList.remove('hidden');
            listView.classList.add('hidden');
        } else {
            singleView.classList.add('hidden');
            listView.classList.remove('hidden');
            this.updateHistoryDisplay();
        }
    }

    async inspectCacheEntry(cacheId) {
        const viewer = this.querySelector('#requestResponseViewer');

        // Show loading state
        viewer.innerHTML = '<div class="loading">Loading cache entry...</div>';

        try {
            const response = await fetch(`/platform/open-router/chat/cache-entry/${cacheId}`);
            const data = await response.json();

            if (data.status === 'success') {
                this.displayCacheEntry(data.data, cacheId);
            } else {
                viewer.innerHTML = `
                    <div class="error-state">
                        <h3>❌ Cache Entry Not Found</h3>
                        <p>Cache ID: ${cacheId}</p>
                        <p>${data.message || 'Entry may have expired or been deleted.'}</p>
                    </div>
                `;
            }
        } catch (error) {
            viewer.innerHTML = `
                <div class="error-state">
                    <h3>❌ Error Loading Cache Entry</h3>
                    <p>${error.message}</p>
                </div>
            `;
        }
    }

    displayCacheEntry(cacheData, cacheId) {
        const viewer = this.querySelector('#requestResponseViewer');

        // Parse the data structure
        const request = cacheData.request;
        const response = cacheData.response;
        const metadata = {
            cachedAt: new Date(cacheData.cached_at).toLocaleString(),
            ttlHours: cacheData.ttl_hours,
            expiresAt: new Date(cacheData.cached_at + (cacheData.ttl_hours * 3600 * 1000)).toLocaleString()
        };

        // Extract key information
        const systemPrompt = request.messages?.find(m => m.role === 'system')?.content || 'No system prompt';
        const userPrompt = request.messages?.find(m => m.role === 'user')?.content || 'No user prompt';
        const assistantResponse = response.choices?.[0]?.message?.content || 'No response';
        const reasoning = response.choices?.[0]?.message?.reasoning || null;

        viewer.innerHTML = `
            <div class="cache-entry-display">
                <!-- Metadata Header -->
                <div class="metadata-header">
                    <div class="cache-id-display">
                        <span class="label">Cache ID:</span>
                        <code>${cacheId}</code>
                        <button onclick="navigator.clipboard.writeText('${cacheId}')">📋</button>
                    </div>
                    <div class="cache-timing">
                        <span>Cached: ${metadata.cachedAt}</span>
                        <span>Expires: ${metadata.expiresAt}</span>
                    </div>
                </div>

                <!-- Request Section -->
                <div class="request-section">
                    <h3>📤 Request</h3>
                    <div class="request-details">
                        <div class="model-info">
                            <span class="label">Model:</span> ${request.model}
                            <span class="label">Provider:</span> ${request.provider?.order?.[0] || 'auto'}
                        </div>
                        <div class="parameters">
                            <span class="label">Temperature:</span> ${request.temperature || 0}
                            <span class="label">Max Tokens:</span> ${request.max_tokens || 'default'}
                        </div>
                    </div>
                    
                    <div class="prompts">
                        <div class="prompt-section">
                            <h4>System Prompt</h4>
                            <pre class="prompt-content">${this.escapeHtml(systemPrompt)}</pre>
                        </div>
                        <div class="prompt-section">
                            <h4>User Prompt</h4>
                            <pre class="prompt-content">${this.escapeHtml(userPrompt)}</pre>
                        </div>
                    </div>
                </div>

                <!-- Response Section -->
                <div class="response-section">
                    <h3>📥 Response</h3>
                    <div class="response-details">
                        <div class="provider-info">
                            <span class="label">Provider Used:</span> ${response.provider}
                            <span class="label">Model:</span> ${response.model}
                        </div>
                        <div class="usage-stats">
                            <span class="label">Prompt Tokens:</span> ${response.usage?.prompt_tokens || 0}
                            <span class="label">Completion Tokens:</span> ${response.usage?.completion_tokens || 0}
                            <span class="label">Total Tokens:</span> ${response.usage?.total_tokens || 0}
                        </div>
                        <div class="cost-info">
                            <span class="label">Total Cost:</span> ${response.cost_breakdown?.total_cost || '$0.00'}
                            <span class="label">Cost/1K:</span> ${response.cost_breakdown?.cost_per_1k || '$0.00'}
                        </div>
                    </div>
                    
                    <div class="response-content">
                        <h4>Assistant Response</h4>
                        <pre class="response-text">${this.escapeHtml(assistantResponse)}</pre>
                        
                        ${reasoning ? `
                            <h4>Reasoning</h4>
                            <pre class="reasoning-text">${this.escapeHtml(reasoning)}</pre>
                        ` : ''}
                    </div>
                </div>

                <!-- Actions -->
                <div class="cache-actions">
                    <button onclick="window.open('/platform/open-router/chat/cache-entry/${cacheId}', '_blank')">
                        🔗 Open Raw JSON
                    </button>
                    <button onclick="navigator.clipboard.writeText(JSON.stringify(${JSON.stringify(cacheData)}, null, 2))">
                        📋 Copy Full JSON
                    </button>
                </div>
            </div>
        `;
    }

    addToHistory(entry) {
        // Add to beginning of array (most recent first)
        this.cacheHistory.unshift({
            ...entry,
            id: `history-${Date.now()}`,
            timestamp: new Date().toISOString()
        });

        // Keep only last 100 entries
        if (this.cacheHistory.length > 100) {
            this.cacheHistory = this.cacheHistory.slice(0, 100);
        }

        // Update display if in list view
        if (this.viewMode === 'list') {
            this.updateHistoryDisplay();
        }

        // Add notification badge
        this.showNotification(`New cache entry: ${entry.type}`);
    }

    updateHistoryDisplay() {
        const container = this.querySelector('#cacheHistoryList');
        const filter = this.querySelector('#typeFilter').value;

        const filteredHistory = filter === 'all'
            ? this.cacheHistory
            : this.cacheHistory.filter(entry => entry.type === filter);

        if (filteredHistory.length === 0) {
            container.innerHTML = '<div class="empty-state">No entries match the selected filter.</div>';
            return;
        }

        container.innerHTML = filteredHistory.map(entry => `
            <div class="history-entry" data-cache-id="${entry.cacheId}">
                <div class="entry-header">
                    <span class="entry-type ${entry.type}">${entry.type}</span>
                    <span class="entry-time">${new Date(entry.timestamp).toLocaleTimeString()}</span>
                </div>
                <div class="entry-preview">${this.escapeHtml(entry.text)}</div>
                <div class="entry-actions">
                    <code class="cache-id-mini">${entry.cacheId}</code>
                    <button data-cache-id="${entry.cacheId}" class="inspect-history-btn">
                        🔍 Inspect
                    </button>
                </div>
            </div>
        `).join('');

        // Add event listeners to the inspect buttons
        container.querySelectorAll('.inspect-history-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.inspectFromHistory(btn.dataset.cacheId);
            });
        });
    }

    inspectFromHistory(cacheId) {
        // Switch to single view and inspect
        this.switchViewMode('single');
        this.querySelector('#cacheIdInput').value = cacheId;
        this.inspectCacheEntry(cacheId);
    }

    filterHistory(type) {
        this.updateHistoryDisplay();
    }

    async loadCacheStats() {
        try {
            const response = await fetch('/cache/stats');
            const data = await response.json();

            if (data.status === 'success') {
                const stats = data.data;

                // Update stat cards
                this.querySelector('.stat-card:nth-child(1) .stat-value').textContent =
                    stats.total_entries || '0';
                this.querySelector('.stat-card:nth-child(2) .stat-value').textContent =
                    stats.dates_distribution?.[new Date().toISOString().split('T')[0].replace(/-/g, '/')] || '0';

                // Calculate estimated cost savings (rough estimate)
                const estimatedSavings = (stats.total_entries * 0.0001).toFixed(4);
                this.querySelector('.stat-card:nth-child(3) .stat-value').textContent =
                    `$${estimatedSavings}`;

                // Mock average response time
                this.querySelector('.stat-card:nth-child(4) .stat-value').textContent = '450ms';
            }
        } catch (error) {
            console.error('Failed to load cache stats:', error);
        }
    }

    showNotification(message) {
        // Simple notification (can be enhanced with better UI)
        const notification = document.createElement('div');
        notification.className = 'cache-notification';
        notification.textContent = message;
        this.appendChild(notification);

        setTimeout(() => notification.remove(), 3000);
    }

    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;'
        };
        return String(text).replace(/[&<>"']/g, char => map[char]);
    }

    // Public method to add cache ID from external source
    addCacheId(cacheId, type = 'manual', text = '') {
        this.addToHistory({ cacheId, type, text });
    }
}