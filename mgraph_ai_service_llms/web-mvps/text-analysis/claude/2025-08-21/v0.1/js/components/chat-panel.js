// Chat Panel Component
import { TextFormatter } from '../utils/text-formatter.js';
import { getRandomSample, getRandomWelcome } from '../utils/sample-texts.js';

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
    
    addMessage(text, sender = 'user') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        bubble.textContent = text;
        
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
}