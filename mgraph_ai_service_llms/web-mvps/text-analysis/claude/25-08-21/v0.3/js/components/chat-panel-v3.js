import { ChatPanel as ChatPanelV1 } from '../../../v0.1/js/components/chat-panel.js';
import { TextFormatter } from '../../../v0.1/js/utils/text-formatter.js';
import { getRandomSample, getRandomWelcome } from '../../../v0.1/js/utils/sample-texts.js';

export class ChatPanel extends ChatPanelV1 {

    // Add a new method for analysis messages with distinct styling
    addAnalysisMessage(text, analysisId, analysisNumber) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message analysis-info';
        messageDiv.dataset.analysisId = analysisId;

        const bubble = document.createElement('div');
        bubble.className = 'message-bubble analysis-bubble clickable';
        bubble.innerHTML = `
            <span class="analysis-icon">📊</span>
            <span class="analysis-text">Analysis #${analysisNumber}: ${text}</span>
            <span class="analysis-click-hint">Click to view details →</span>
        `;

        const time = document.createElement('div');
        time.className = 'message-time';
        time.textContent = TextFormatter.formatTimestamp(new Date());

        messageDiv.appendChild(bubble);
        messageDiv.appendChild(time);

        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();

        // Store message with type
        this.messages.push({
            text,
            sender: 'analysis',
            analysisId: analysisId,
            analysisNumber: analysisNumber,
            time: new Date()
        });

        // Add click handler
        bubble.addEventListener('click', () => {
            // Visual feedback
            bubble.classList.add('clicked');
            setTimeout(() => bubble.classList.remove('clicked'), 200);

            // Emit event to show this analysis
            this.dispatchEvent(new CustomEvent('analysis-clicked', {
                detail: { analysisId: analysisId },
                bubbles: true
            }));
        });
    }

    // Override the original addMessage to handle different message types better
    addMessage(text, sender = 'user') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;

        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';

        // Add icon for system messages
        if (sender === 'system') {
            bubble.innerHTML = `<span class="message-text">${text}</span>`;
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

        // Store message
        this.messages.push({
            text,
            sender,
            time: new Date()
        });
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
}