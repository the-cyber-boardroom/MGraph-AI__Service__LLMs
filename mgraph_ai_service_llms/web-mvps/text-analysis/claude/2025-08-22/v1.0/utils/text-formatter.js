// mgraph_ai_service_llms/web-mvps/text-analysis/v1.0/utils/text-formatter.js

export class TextFormatter {
    static truncate(text, maxLength = 100) {
        if (!text) return '';
        return text.length > maxLength
            ? text.substring(0, maxLength) + '...'
            : text;
    }

    static highlightNumbers(text) {
        if (!text) return '';
        // Highlight numbers, percentages, and currency
        return text.replace(
            /(\$?\d+(?:,\d{3})*(?:\.\d+)?%?|\d+%)/g,
            '<span class="highlight">$1</span>'
        );
    }

    static formatTimestamp(date) {
        if (!date) date = new Date();
        return new Intl.DateTimeFormat('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        }).format(date);
    }

    static formatDate(date) {
        if (!date) date = new Date();
        return new Intl.DateTimeFormat('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(date);
    }

    static escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;',
            '/': '&#x2F;'
        };
        return text.replace(/[&<>"'/]/g, char => map[char]);
    }

    static extractFirstSentence(text) {
        if (!text) return '';
        const match = text.match(/^[^.!?]+[.!?]/);
        return match ? match[0] : text;
    }

    static wordCount(text) {
        if (!text) return 0;
        return text.trim().split(/\s+/).length;
    }

    static characterCount(text) {
        return text ? text.length : 0;
    }

    static capitalizeFirst(text) {
        if (!text) return '';
        return text.charAt(0).toUpperCase() + text.slice(1);
    }

    static formatList(items, separator = ', ') {
        if (!items || items.length === 0) return '';
        if (items.length === 1) return items[0];
        if (items.length === 2) return items.join(' and ');
        return items.slice(0, -1).join(separator) + ', and ' + items[items.length - 1];
    }

    static formatResponseTime(ms) {
        if (ms < 1000) return `${ms}ms`;
        return `${(ms / 1000).toFixed(2)}s`;
    }

    static validateTextLength(text, min = 10, max = 8000) {
        const length = text ? text.length : 0;
        return {
            isValid: length >= min && length <= max,
            length,
            min,
            max,
            message: length < min
                ? `Text must be at least ${min} characters`
                : length > max
                    ? `Text must be less than ${max} characters`
                    : 'Valid length'
        };
    }
}