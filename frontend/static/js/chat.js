/**
 * Chat Module with Voice Support
 * Handles chat functionality with bilingual speech recognition and synthesis
 */

class ChatManager {
    constructor() {
        this.sessionId = this.generateSessionId();
        this.speechManager = window.speechManager;
        this.currentLanguage = window.i18n.getCurrentLanguage();

        // UI Elements
        this.elements = {
            chatMessages: document.getElementById('chat-messages'),
            chatInput: document.getElementById('chat-input'),
            sendButton: document.getElementById('send-button'),
            micButton: document.getElementById('mic-button'),
            recordingIndicator: document.getElementById('recording-indicator'),
            speechFeedback: document.getElementById('speech-feedback'),
            speechText: document.getElementById('speech-text'),
            voiceStatus: document.getElementById('voice-status'),
            voiceSettingsBtn: document.getElementById('voice-settings-btn'),
            voiceControls: document.getElementById('voice-controls'),
            autoSpeakCheckbox: document.getElementById('auto-speak'),
            voiceCommandsCheckbox: document.getElementById('voice-commands'),
            speechRateSlider: document.getElementById('speech-rate'),
            speechRateValue: document.getElementById('speech-rate-value'),
            speechWarning: document.getElementById('speech-warning'),
            speechLangSelector: document.getElementById('speech-lang-selector')
        };

        // Voice settings
        this.voiceSettings = {
            autoSpeak: false,
            voiceCommands: false,
            speechRate: 1.0,
            speechLanguage: this.currentLanguage
        };

        // Chat state
        this.isProcessing = false;
        this.isRecording = false;

        this.init();
    }

    async init() {
        console.log('🤖 Initializing Chat Manager...');

        // Check speech support
        await this.checkSpeechSupport();

        // Setup event listeners
        this.setupEventListeners();

        // Setup speech callbacks
        this.setupSpeechCallbacks();

        // Load settings from localStorage
        this.loadSettings();

        // Setup voice controls
        this.setupVoiceControls();

        console.log('✅ Chat Manager initialized');
    }

    async checkSpeechSupport() {
        if (!this.speechManager.isSpeechSupported()) {
            console.warn('🎤 Speech features not supported');
            if (this.elements.speechWarning) {
                this.elements.speechWarning.classList.remove('hidden');
            }
            if (this.elements.micButton) {
                this.elements.micButton.disabled = true;
                this.elements.micButton.title = 'Speech not supported in this browser';
            }
        } else {
            // Test speech functionality
            const testResults = await this.speechManager.testSpeech();
            console.log('🎤 Speech test results:', testResults);

            if (!testResults.hindiVoiceAvailable || !testResults.englishVoiceAvailable) {
                console.warn('🎤 Some language voices may not be available');
            }
        }
    }

    setupEventListeners() {
        // Send button
        if (this.elements.sendButton) {
            this.elements.sendButton.addEventListener('click', () => {
                this.handleSendMessage();
            });
        }

        // Enter key in input
        if (this.elements.chatInput) {
            this.elements.chatInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.handleSendMessage();
                }
            });

            // Auto-resize textarea
            this.elements.chatInput.addEventListener('input', () => {
                this.autoResizeTextarea();
            });
        }

        // Microphone button
        if (this.elements.micButton) {
            this.elements.micButton.addEventListener('click', () => {
                this.toggleRecording();
            });

            // Long press for language selection
            let pressTimer;
            this.elements.micButton.addEventListener('mousedown', () => {
                pressTimer = setTimeout(() => {
                    this.showLanguageSelector();
                }, 500);
            });

            this.elements.micButton.addEventListener('mouseup', () => {
                clearTimeout(pressTimer);
            });

            this.elements.micButton.addEventListener('mouseleave', () => {
                clearTimeout(pressTimer);
            });

            // Touch events for mobile
            this.elements.micButton.addEventListener('touchstart', (e) => {
                e.preventDefault();
                pressTimer = setTimeout(() => {
                    this.showLanguageSelector();
                }, 500);
            });

            this.elements.micButton.addEventListener('touchend', (e) => {
                e.preventDefault();
                clearTimeout(pressTimer);
                if (!this.isRecording) {
                    this.toggleRecording();
                }
            });
        }

        // Quick question buttons
        document.querySelectorAll('.quick-question').forEach(button => {
            button.addEventListener('click', () => {
                const question = button.getAttribute('data-question');
                const lang = button.getAttribute('data-lang');
                this.sendQuickQuestion(question, lang);
            });
        });

        // Language selector buttons
        document.querySelectorAll('.speech-lang-btn').forEach(button => {
            button.addEventListener('click', () => {
                const lang = button.getAttribute('data-lang');
                this.setSpeechLanguage(lang);
                this.hideLanguageSelector();
            });
        }

        // Voice settings button
        if (this.elements.voiceSettingsBtn) {
            this.elements.voiceSettingsBtn.addEventListener('click', () => {
                this.toggleVoiceSettings();
            });
        }

        // Settings controls
        if (this.elements.autoSpeakCheckbox) {
            this.elements.autoSpeakCheckbox.addEventListener('change', (e) => {
                this.voiceSettings.autoSpeak = e.target.checked;
                this.saveSettings();
            });
        }

        if (this.elements.voiceCommandsCheckbox) {
            this.elements.voiceCommandsCheckbox.addEventListener('change', (e) => {
                this.voiceSettings.voiceCommands = e.target.checked;
                this.saveSettings();
            });
        }

        if (this.elements.speechRateSlider) {
            this.elements.speechRateSlider.addEventListener('input', (e) => {
                this.voiceSettings.speechRate = parseFloat(e.target.value);
                if (this.elements.speechRateValue) {
                    this.elements.speechRateValue.textContent = `${this.voiceSettings.speechRate}x`;
                }
                this.saveSettings();
            });
        }

        // Speak response buttons
        document.addEventListener('click', (e) => {
            if (e.target.closest('.speak-response')) {
                const messageElement = e.target.closest('.chat-message').querySelector('.message-text');
                if (messageElement) {
                    const text = messageElement.textContent;
                    const language = messageElement.getAttribute('data-lang') || this.currentLanguage;
                    this.speakResponse(text, language);
                }
            }
        });

        // Click outside to close language selector
        document.addEventListener('click', (e) => {
            if (!e.target.closest('#mic-button') && !e.target.closest('#speech-lang-selector')) {
                this.hideLanguageSelector();
            }
        });
    }

    setupSpeechCallbacks() {
        if (!this.speechManager) return;

        // Speech recognition callbacks
        this.speechManager.onResult = (result) => {
            this.handleSpeechResult(result);
        };

        this.speechManager.onStart = () => {
            this.handleRecordingStart();
        };

        this.speechManager.onEnd = () => {
            this.handleRecordingEnd();
        };

        this.speechManager.onSpeechStart = () => {
            this.handleUserSpeakingStart();
        };

        this.speechManager.onSpeechEnd = () => {
            this.handleUserSpeakingEnd();
        };

        this.speechManager.onError = (error) => {
            this.handleSpeechError(error);
        };
    }

    setupVoiceControls() {
        // Update UI with current settings
        if (this.elements.autoSpeakCheckbox) {
            this.elements.autoSpeakCheckbox.checked = this.voiceSettings.autoSpeak;
        }
        if (this.elements.voiceCommandsCheckbox) {
            this.elements.voiceCommandsCheckbox.checked = this.voiceSettings.voiceCommands;
        }
        if (this.elements.speechRateSlider) {
            this.elements.speechRateSlider.value = this.voiceSettings.speechRate;
        }
        if (this.elements.speechRateValue) {
            this.elements.speechRateValue.textContent = `${this.voiceSettings.speechRate}x`;
        }
    }

    async handleSendMessage() {
        const message = this.elements.chatInput.value.trim();
        if (!message || this.isProcessing) return;

        this.clearInput();
        await this.sendUserMessage(message);
    }

    async sendQuickQuestion(question, language) {
        if (this.isProcessing) return;

        // Update language if needed
        if (language && language !== this.currentLanguage) {
            window.i18n.setLanguage(language);
            this.currentLanguage = language;
        }

        await this.sendUserMessage(question);
    }

    async sendUserMessage(message) {
        this.isProcessing = true;
        this.updateSendButtonState(false);

        // Add user message to chat
        this.addMessageToChat(message, 'user', this.currentLanguage);

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Send to API
            const response = await window.api.chat.sendMessage(message, this.currentLanguage, this.sessionId);

            if (response.success !== false) {
                // Add bot response to chat
                this.addMessageToChat(response.response, 'bot', response.language, response.context_tags);

                // Auto-speak if enabled
                if (this.voiceSettings.autoSpeak) {
                    this.speakResponse(response.response, response.language);
                }

                // Update session ID
                if (response.session_id) {
                    this.sessionId = response.session_id;
                }
            } else {
                this.showError(response.message || 'Failed to get response');
            }

        } catch (error) {
            console.error('Failed to send message:', error);
            this.showError('Network error. Please try again.');
        } finally {
            this.hideTypingIndicator();
            this.isProcessing = false;
            this.updateSendButtonState(true);
        }
    }

    async toggleRecording() {
        if (!this.speechManager.isSpeechSupported()) {
            this.showError('Speech recognition not supported in this browser');
            return;
        }

        if (this.isRecording) {
            this.stopRecording();
        } else {
            await this.startRecording();
        }
    }

    async startRecording() {
        try {
            this.isRecording = true;
            this.updateMicButtonState(true);
            this.updateVoiceStatus('listening');

            await this.speechManager.startRecording(this.voiceSettings.speechLanguage);

        } catch (error) {
            console.error('Failed to start recording:', error);
            this.isRecording = false;
            this.updateMicButtonState(false);
            this.updateVoiceStatus('ready');
            this.showError(error.message || 'Failed to start recording');
        }
    }

    stopRecording() {
        this.speechManager.stopRecording();
    }

    handleRecordingStart() {
        console.log('🎤 Recording started');
        this.updateVoiceStatus('listening');
    }

    handleRecordingEnd() {
        console.log('🎤 Recording ended');
        this.isRecording = false;
        this.updateMicButtonState(false);
        this.hideSpeechFeedback();
        this.updateVoiceStatus('thinking');
    }

    handleUserSpeakingStart() {
        this.updateVoiceStatus('listening');
        if (this.elements.speechFeedback) {
            this.elements.speechFeedback.classList.remove('hidden');
            this.elements.speechText.textContent = 'Listening...';
        }
    }

    handleUserSpeakingEnd() {
        this.updateVoiceStatus('thinking');
        if (this.elements.speechText) {
            this.elements.speechText.textContent = 'Processing...';
        }
    }

    handleSpeechResult(result) {
        console.log('🎤 Speech result:', result);

        if (result.finalTranscript) {
            // Set the recognized text to input
            this.elements.chatInput.value = result.finalTranscript;
            this.autoResizeTextarea();

            // Update speech feedback
            if (this.elements.speechText) {
                this.elements.speechText.textContent = result.finalTranscript;
            }

            // Check for voice commands if enabled
            if (this.voiceSettings.voiceCommands) {
                this.processVoiceCommand(result.finalTranscript);
            }

            // Auto-send after a short delay
            setTimeout(() => {
                if (result.finalTranscript.trim()) {
                    this.handleSendMessage();
                }
            }, 500);
        } else if (result.interimTranscript) {
            // Show interim results
            if (this.elements.speechText) {
                this.elements.speechText.textContent = result.interimTranscript;
            }
        }
    }

    handleSpeechError(error) {
        console.error('🎤 Speech error:', error);
        this.isRecording = false;
        this.updateMicButtonState(false);
        this.updateVoiceStatus('ready');
        this.hideSpeechFeedback();
        this.showError(error.message || 'Speech recognition error');
    }

    processVoiceCommand(text) {
        const command = text.toLowerCase().trim();
        const language = this.voiceSettings.speechLanguage;

        // Voice commands in English
        if (language === 'en') {
            if (command.includes('clear') || command.includes('delete')) {
                this.clearChat();
                return true;
            } else if (command.includes('hindi') || command.includes('switch to hindi')) {
                this.setSpeechLanguage('hi');
                window.i18n.setLanguage('hi');
                return true;
            } else if (command.includes('english') || command.includes('switch to english')) {
                this.setSpeechLanguage('en');
                window.i18n.setLanguage('en');
                return true;
            } else if (command.includes('stop speaking') || command.includes('quiet')) {
                this.speechManager.stopSpeaking();
                return true;
            }
        }
        // Voice commands in Hindi
        else if (language === 'hi') {
            if (command.includes('साफ') || command.includes('हटाओ')) {
                this.clearChat();
                return true;
            } else if (command.includes('अंग्रेजी') || command.includes('इंग्लिश')) {
                this.setSpeechLanguage('en');
                window.i18n.setLanguage('en');
                return true;
            } else if (command.includes('हिंदी')) {
                this.setSpeechLanguage('hi');
                window.i18n.setLanguage('hi');
                return true;
            } else if (command.includes('चुप') || command.includes('बोलना बंद')) {
                this.speechManager.stopSpeaking();
                return true;
            }
        }

        return false;
    }

    speakResponse(text, language = null) {
        if (!this.speechManager.isSpeechSupported()) return;

        const speechLanguage = language || this.currentLanguage;
        this.updateVoiceStatus('speaking');

        this.speechManager.speak(text, speechLanguage, {
            rate: this.voiceSettings.speechRate,
            onStart: () => {
                this.updateVoiceStatus('speaking');
            },
            onEnd: () => {
                this.updateVoiceStatus('ready');
            },
            onError: () => {
                this.updateVoiceStatus('ready');
            }
        });
    }

    showLanguageSelector() {
        if (this.elements.speechLangSelector) {
            this.elements.speechLangSelector.classList.remove('hidden');
        }
    }

    hideLanguageSelector() {
        if (this.elements.speechLangSelector) {
            this.elements.speechLangSelector.classList.add('hidden');
        }
    }

    setSpeechLanguage(language) {
        this.voiceSettings.speechLanguage = language;
        this.speechManager.setLanguage(language);
        this.saveSettings();
        console.log('🎤 Speech language set to:', language);
    }

    toggleVoiceSettings() {
        if (this.elements.voiceControls) {
            const isHidden = this.elements.voiceControls.classList.contains('hidden');
            if (isHidden) {
                this.elements.voiceControls.classList.remove('hidden');
            } else {
                this.elements.voiceControls.classList.add('hidden');
            }
        }
    }

    addMessageToChat(text, sender, language = 'en', contextTags = []) {
        if (!this.elements.chatMessages) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message flex items-start space-x-3 ${sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''} fade-in`;

        const isHindi = language === 'hi';

        // Avatar
        const avatarDiv = document.createElement('div');
        avatarDiv.className = `w-8 h-8 ${sender === 'user' ? 'bg-green-600' : 'bg-blue-600'} rounded-full flex items-center justify-center flex-shrink-0`;
        avatarDiv.innerHTML = `<i class="fas fa-${sender === 'user' ? 'user' : 'robot'} text-white text-sm"></i>`;

        // Message content
        const contentDiv = document.createElement('div');
        contentDiv.className = `max-w-md ${sender === 'user' ? 'bg-green-600 text-white' : 'bg-white text-gray-800'} rounded-lg p-3 shadow-sm`;

        const messageText = document.createElement('p');
        messageText.className = 'message-text';
        messageText.textContent = text;
        messageText.setAttribute('data-lang', language);
        messageText.setAttribute('lang', isHindi ? 'hi' : 'en');

        contentDiv.appendChild(messageText);

        // Add speak button for bot messages
        if (sender === 'bot' && this.speechManager.isSpeechSupported()) {
            const speakButton = document.createElement('button');
            speakButton.className = 'speak-response mt-2 text-blue-600 hover:text-blue-800 text-sm flex items-center space-x-1';
            speakButton.innerHTML = `
                <i class="fas fa-volume-up"></i>
                <span>${window.t('chat.speak_message')}</span>
            `;
            contentDiv.appendChild(speakButton);
        }

        // Add timestamp
        const timestamp = document.createElement('div');
        timestamp.className = 'text-xs text-gray-500 mt-1';
        timestamp.textContent = new Date().toLocaleTimeString();

        // Assemble message
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);
        if (sender === 'user') {
            messageDiv.appendChild(timestamp);
        } else {
            contentDiv.appendChild(timestamp);
        }

        this.elements.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    showTypingIndicator() {
        if (!this.elements.chatMessages) return;

        const indicatorDiv = document.createElement('div');
        indicatorDiv.id = 'typing-indicator';
        indicatorDiv.className = 'chat-message flex items-start space-x-3 fade-in';

        indicatorDiv.innerHTML = `
            <div class="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0">
                <i class="fas fa-robot text-white text-sm"></i>
            </div>
            <div class="bg-white rounded-lg p-3 shadow-sm">
                <div class="flex space-x-1">
                    <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
                    <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
                    <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
                </div>
            </div>
        `;

        this.elements.chatMessages.appendChild(indicatorDiv);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    updateMicButtonState(isRecording) {
        if (!this.elements.micButton || !this.elements.recordingIndicator) return;

        if (isRecording) {
            this.elements.micButton.classList.add('bg-red-500', 'hover:bg-red-600');
            this.elements.micButton.classList.remove('bg-gray-100', 'hover:bg-gray-200');
            this.elements.recordingIndicator.classList.remove('hidden');
        } else {
            this.elements.micButton.classList.remove('bg-red-500', 'hover:bg-red-600');
            this.elements.micButton.classList.add('bg-gray-100', 'hover:bg-gray-200');
            this.elements.recordingIndicator.classList.add('hidden');
        }
    }

    updateSendButtonState(enabled) {
        if (!this.elements.sendButton) return;

        if (enabled) {
            this.elements.sendButton.disabled = false;
            this.elements.sendButton.classList.remove('opacity-50', 'cursor-not-allowed');
        } else {
            this.elements.sendButton.disabled = true;
            this.elements.sendButton.classList.add('opacity-50', 'cursor-not-allowed');
        }
    }

    updateVoiceStatus(status) {
        if (!this.elements.voiceStatus) return;

        const statusText = window.t(`chat.voice_status.${status}`) || status;
        const statusSpan = this.elements.voiceStatus.querySelector('span');
        if (statusSpan) {
            statusSpan.textContent = statusText;
        }

        // Update indicator color
        const indicator = this.elements.voiceStatus.querySelector('div');
        if (indicator) {
            indicator.className = 'w-2 h-2 rounded-full';
            switch (status) {
                case 'ready':
                    indicator.classList.add('bg-green-400');
                    break;
                case 'listening':
                    indicator.classList.add('bg-red-400', 'animate-pulse');
                    break;
                case 'thinking':
                    indicator.classList.add('bg-yellow-400', 'animate-pulse');
                    break;
                case 'speaking':
                    indicator.classList.add('bg-blue-400', 'animate-pulse');
                    break;
                default:
                    indicator.classList.add('bg-gray-400');
            }
        }
    }

    hideSpeechFeedback() {
        if (this.elements.speechFeedback) {
            this.elements.speechFeedback.classList.add('hidden');
        }
    }

    autoResizeTextarea() {
        if (!this.elements.chatInput) return;

        this.elements.chatInput.style.height = 'auto';
        this.elements.chatInput.style.height = Math.min(this.elements.chatInput.scrollHeight, 120) + 'px';
    }

    clearInput() {
        if (this.elements.chatInput) {
            this.elements.chatInput.value = '';
            this.elements.chatInput.style.height = 'auto';
        }
    }

    scrollToBottom() {
        if (this.elements.chatMessages) {
            this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
        }
    }

    clearChat() {
        if (this.elements.chatMessages) {
            // Keep only the welcome message
            const messages = this.elements.chatMessages.querySelectorAll('.chat-message');
            messages.forEach((msg, index) => {
                if (index > 0) { // Keep first message (welcome)
                    msg.remove();
                }
            });
        }
    }

    showError(message) {
        window.showError(message);
    }

    saveSettings() {
        localStorage.setItem('cropgpt_voice_settings', JSON.stringify(this.voiceSettings));
    }

    loadSettings() {
        const saved = localStorage.getItem('cropgpt_voice_settings');
        if (saved) {
            try {
                this.voiceSettings = { ...this.voiceSettings, ...JSON.parse(saved) };
                this.setupVoiceControls();
            } catch (error) {
                console.error('Failed to load voice settings:', error);
            }
        }
    }

    generateSessionId() {
        return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    // Public methods
    setLanguage(language) {
        this.currentLanguage = language;
        this.voiceSettings.speechLanguage = language;
        this.speechManager.setLanguage(language);
        this.saveSettings();
    }

    destroy() {
        if (this.speechManager) {
            this.speechManager.stopRecording();
            this.speechManager.stopSpeaking();
        }
    }
}

// Initialize chat manager when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Wait for i18n to be ready
    setTimeout(() => {
        if (window.i18n && window.i18n.isReady) {
            window.chatManager = new ChatManager();
        } else {
            console.error('❌ i18n not ready, cannot initialize chat');
        }
    }, 1000);
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.chatManager) {
        window.chatManager.destroy();
    }
});