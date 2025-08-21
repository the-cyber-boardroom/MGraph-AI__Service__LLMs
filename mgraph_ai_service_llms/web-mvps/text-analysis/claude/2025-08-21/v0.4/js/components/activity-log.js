export class ActivityLog extends HTMLElement {
    constructor() {
        super();
        this.activities = [];
        this.maxActivities = 50;
    }

    connectedCallback() {
        this.render();
    }

    render() {
        this.className = 'activity-log';
        this.innerHTML = `
            <div class="activity-header">
                <h4>Activity Log</h4>
                <button class="clear-log-btn" title="Clear log">×</button>
            </div>
            <div class="activity-list" id="activityList">
                <div class="activity-item info">
                    <span class="activity-icon">ℹ️</span>
                    <span class="activity-text">Ready to analyze text...</span>
                    <span class="activity-time">${this.formatTime(new Date())}</span>
                </div>
            </div>
        `;

        this.activityList = this.querySelector('#activityList');

        // Clear button handler
        this.querySelector('.clear-log-btn').addEventListener('click', () => {
            this.clear();
        });
    }

    addActivity(message, type = 'info') {
        const activity = {
            message,
            type,
            timestamp: new Date()
        };

        this.activities.push(activity);

        // Keep only the last N activities
        if (this.activities.length > this.maxActivities) {
            this.activities.shift();
        }

        this.appendActivityToDOM(activity);
        this.scrollToBottom();
    }

    appendActivityToDOM(activity) {
        const item = document.createElement('div');
        item.className = `activity-item ${activity.type}`;

        const icon = this.getIconForType(activity.type);

        item.innerHTML = `
            <span class="activity-icon">${icon}</span>
            <span class="activity-text">${this.escapeHtml(activity.message)}</span>
            <span class="activity-time">${this.formatTime(activity.timestamp)}</span>
        `;

        this.activityList.appendChild(item);

        // Remove oldest item if too many
        while (this.activityList.children.length > this.maxActivities) {
            this.activityList.removeChild(this.activityList.firstChild);
        }

        // Add fade-in animation
        item.style.animation = 'fadeIn 0.3s ease-in';
    }

    getIconForType(type) {
        const icons = {
            'info': 'ℹ️',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌',
            'llm': '🤖',
            'search': '🔍',
            'processing': '⚙️'
        };
        return icons[type] || 'ℹ️';
    }

    formatTime(date) {
        return new Intl.DateTimeFormat('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        }).format(date);
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

    scrollToBottom() {
        setTimeout(() => {
            this.activityList.scrollTop = this.activityList.scrollHeight;
        }, 50);
    }

    clear() {
        this.activities = [];
        this.activityList.innerHTML = `
            <div class="activity-item info">
                <span class="activity-icon">ℹ️</span>
                <span class="activity-text">Log cleared</span>
                <span class="activity-time">${this.formatTime(new Date())}</span>
            </div>
        `;
    }
}