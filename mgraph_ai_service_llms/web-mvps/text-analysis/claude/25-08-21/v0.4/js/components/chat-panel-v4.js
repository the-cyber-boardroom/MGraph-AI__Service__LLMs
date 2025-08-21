import { ChatPanel as ChatPanelV3 } from '../../../v0.3/js/components/chat-panel-v3.js';
import { TextFormatter } from '../../../v0.1/js/utils/text-formatter.js';

export class ChatPanel extends ChatPanelV3 {

    // Override to add "Generate Answer" option to question messages
    addMessage(text, sender = 'user') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;

        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';

        // Check if this is a question from the user
        const isQuestion = sender === 'user' && text.endsWith('?');

        if (sender === 'system') {
            bubble.innerHTML = `<span class="message-text">${text}</span>`;
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

        // Store message
        this.messages.push({
            text,
            sender,
            time: new Date()
        });

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
                        this.addMessage(data.response_text, 'system');

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
}