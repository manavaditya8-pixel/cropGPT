/**
 * Speech Recognition and Synthesis Module
 * Bilingual voice functionality for CropGPT chatbot
 */

class SpeechManager {
    constructor() {
        this.isSupported = this.checkSupport();
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.isRecording = false;
        this.currentLanguage = 'en';

        // Speech recognition settings
        this.continuous = false;
        this.interimResults = true;
        this.maxAlternatives = 1;

        // Event callbacks
        this.onResult = null;
        this.onStart = null;
        this.onEnd = null;
        this.onError = null;
        this.onSpeechStart = null;
        this.onSpeechEnd = null;

        console.log('🎤 Speech Manager initialized. Support:', this.isSupported);
    }

    /**
     * Check browser support for speech APIs
     */
    checkSupport() {
        const hasRecognition = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
        const hasSynthesis = 'speechSynthesis' in window;
        const hasMediaRecorder = 'MediaRecorder' in window;

        return hasRecognition && hasSynthesis && hasMediaRecorder;
    }

    /**
     * Initialize speech recognition
     */
    initializeRecognition() {
        if (!this.isSupported) {
            throw new Error('Speech APIs are not supported in this browser');
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();

        // Configure recognition
        this.recognition.continuous = this.continuous;
        this.recognition.interimResults = this.interimResults;
        this.recognition.maxAlternatives = this.maxAlternatives;
        this.recognition.lang = this.getLanguageCode(this.currentLanguage);

        // Event handlers
        this.recognition.onstart = () => {
            console.log('🎤 Speech recognition started');
            this.isRecording = true;
            if (this.onStart) this.onStart();
        };

        this.recognition.onend = () => {
            console.log('🎤 Speech recognition ended');
            this.isRecording = false;
            if (this.onEnd) this.onEnd();
        };

        this.recognition.onspeechstart = () => {
            console.log('🎤 User started speaking');
            if (this.onSpeechStart) this.onSpeechStart();
        };

        this.recognition.onspeechend = () => {
            console.log('🎤 User stopped speaking');
            if (this.onSpeechEnd) this.onSpeechEnd();
        };

        this.recognition.onresult = (event) => {
            console.log('🎤 Speech recognition result:', event);
            this.handleResult(event);
        };

        this.recognition.onerror = (event) => {
            console.error('🎤 Speech recognition error:', event.error);
            this.handleError(event.error);
        };
    }

    /**
     * Get language code for speech recognition
     */
    getLanguageCode(language) {
        const languageCodes = {
            'en': 'en-IN',
            'hi': 'hi-IN',
            'en-US': 'en-US',
            'hi-IN': 'hi-IN'
        };

        // Default to Indian English for agricultural context
        return languageCodes[language] || 'en-IN';
    }

    /**
     * Handle speech recognition results
     */
    handleResult(event) {
        let finalTranscript = '';
        let interimTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;

            if (event.results[i].isFinal) {
                finalTranscript += transcript;
            } else {
                interimTranscript += transcript;
            }
        }

        const result = {
            finalTranscript: finalTranscript.trim(),
            interimTranscript: interimTranscript.trim(),
            confidence: event.results[event.results.length - 1] ?
                       event.results[event.results.length - 1][0].confidence : 0,
            language: this.currentLanguage
        };

        console.log('🎤 Speech result:', result);

        if (this.onResult) {
            this.onResult(result);
        }
    }

    /**
     * Handle speech recognition errors
     */
    handleError(error) {
        const errorMessages = {
            'no-speech': 'No speech detected. Please try again.',
            'audio-capture': 'Microphone not available. Please check permissions.',
            'not-allowed': 'Microphone permission denied. Please allow microphone access.',
            'network': 'Network error. Please check your internet connection.',
            'service-not-allowed': 'Speech recognition service not allowed.',
            'aborted': 'Speech recognition was aborted.'
        };

        const message = errorMessages[error] || `Speech recognition error: ${error}`;
        console.error('🎤 Speech error:', error, message);

        if (this.onError) {
            this.onError({
                type: 'recognition_error',
                error: error,
                message: message
            });
        }
    }

    /**
     * Start speech recognition
     */
    async startRecording(language = null) {
        if (!this.isSupported) {
            throw new Error('Speech recognition is not supported');
        }

        if (this.isRecording) {
            console.warn('🎤 Already recording');
            return;
        }

        if (language) {
            this.currentLanguage = language;
        }

        // Initialize recognition if not already done
        if (!this.recognition) {
            this.initializeRecognition();
        }

        // Update language setting
        this.recognition.lang = this.getLanguageCode(this.currentLanguage);

        try {
            // Request microphone permission
            await this.requestMicrophonePermission();

            // Start recognition
            this.recognition.start();
            console.log('🎤 Started recording in', this.currentLanguage);
        } catch (error) {
            console.error('🎤 Failed to start recording:', error);
            throw error;
        }
    }

    /**
     * Stop speech recognition
     */
    stopRecording() {
        if (this.recognition && this.isRecording) {
            this.recognition.stop();
            console.log('🎤 Stopped recording');
        }
    }

    /**
     * Abort speech recognition
     */
    abortRecording() {
        if (this.recognition && this.isRecording) {
            this.recognition.abort();
            console.log('🎤 Aborted recording');
        }
    }

    /**
     * Request microphone permission
     */
    async requestMicrophonePermission() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            stream.getTracks().forEach(track => track.stop());
            return true;
        } catch (error) {
            console.error('🎤 Microphone permission denied:', error);
            throw new Error('Microphone permission denied. Please allow microphone access to use voice features.');
        }
    }

    /**
     * Text-to-speech synthesis
     */
    speak(text, language = null, options = {}) {
        if (!this.isSupported) {
            throw new Error('Speech synthesis is not supported');
        }

        // Cancel any ongoing speech
        this.stopSpeaking();

        const utterance = new SpeechSynthesisUtterance(text);

        // Set language
        const speechLanguage = language || this.currentLanguage;
        utterance.lang = this.getLanguageCode(speechLanguage);

        // Set voice options
        utterance.rate = options.rate || 1.0;
        utterance.pitch = options.pitch || 1.0;
        utterance.volume = options.volume || 1.0;

        // Select appropriate voice
        const voice = this.selectVoice(speechLanguage);
        if (voice) {
            utterance.voice = voice;
        }

        // Event handlers
        utterance.onstart = () => {
            console.log('🔊 Started speaking');
            if (options.onStart) options.onStart();
        };

        utterance.onend = () => {
            console.log('🔊 Finished speaking');
            if (options.onEnd) options.onEnd();
        };

        utterance.onerror = (event) => {
            console.error('🔊 Speech synthesis error:', event);
            if (options.onError) options.onError(event);
        };

        // Speak
        this.synthesis.speak(utterance);
        console.log('🔊 Speaking:', text, 'Language:', speechLanguage);
    }

    /**
     * Stop speech synthesis
     */
    stopSpeaking() {
        if (this.synthesis.speaking) {
            this.synthesis.cancel();
            console.log('🔊 Stopped speaking');
        }
    }

    /**
     * Pause speech synthesis
     */
    pauseSpeaking() {
        if (this.synthesis.speaking && !this.synthesis.paused) {
            this.synthesis.pause();
            console.log('🔊 Paused speaking');
        }
    }

    /**
     * Resume speech synthesis
     */
    resumeSpeaking() {
        if (this.synthesis.paused) {
            this.synthesis.resume();
            console.log('🔊 Resumed speaking');
        }
    }

    /**
     * Select appropriate voice for language
     */
    selectVoice(language) {
        const voices = this.synthesis.getVoices();
        const languageCode = this.getLanguageCode(language);

        // Try to find exact match
        let voice = voices.find(v => v.lang === languageCode);

        // Try language family match
        if (!voice) {
            const langPrefix = languageCode.split('-')[0];
            voice = voices.find(v => v.lang.startsWith(langPrefix));
        }

        // Fallback to default voice
        if (!voice && voices.length > 0) {
            voice = voices[0];
        }

        return voice;
    }

    /**
     * Get available voices
     */
    getAvailableVoices() {
        if (!this.isSupported) {
            return [];
        }

        const voices = this.synthesis.getVoices();
        return voices.map(voice => ({
            name: voice.name,
            lang: voice.lang,
            localService: voice.localService,
            default: voice.default
        }));
    }

    /**
     * Set language for speech operations
     */
    setLanguage(language) {
        this.currentLanguage = language;

        // Update recognition language if active
        if (this.recognition) {
            this.recognition.lang = this.getLanguageCode(language);
        }

        console.log('🎤 Language set to:', language);
    }

    /**
     * Get current language
     */
    getLanguage() {
        return this.currentLanguage;
    }

    /**
     * Check if currently recording
     */
    isCurrentlyRecording() {
        return this.isRecording;
    }

    /**
     * Check if currently speaking
     */
    isCurrentlySpeaking() {
        return this.synthesis.speaking;
    }

    /**
     * Check if speech is supported
     */
    isSpeechSupported() {
        return this.isSupported;
    }

    /**
     * Get browser compatibility info
     */
    getCompatibilityInfo() {
        return {
            speechRecognition: 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window,
            speechSynthesis: 'speechSynthesis' in window,
            mediaRecorder: 'MediaRecorder' in window,
            getUserMedia: 'getUserMedia' in navigator.mediaDevices,
            recommendedBrowser: this.getRecommendedBrowser()
        };
    }

    /**
     * Get recommended browser for best speech support
     */
    getRecommendedBrowser() {
        const userAgent = navigator.userAgent;

        if (userAgent.includes('Chrome')) {
            return 'Google Chrome (Recommended)';
        } else if (userAgent.includes('Firefox')) {
            return 'Mozilla Firefox (Limited support)';
        } else if (userAgent.includes('Safari')) {
            return 'Safari (Limited support)';
        } else if (userAgent.includes('Edge')) {
            return 'Microsoft Edge (Good support)';
        }

        return 'Chrome or Edge recommended for best speech support';
    }

    /**
     * Test speech functionality
     */
    async testSpeech() {
        const results = {
            recognitionSupported: false,
            synthesisSupported: false,
            microphonePermission: false,
            voicesAvailable: 0,
            hindiVoiceAvailable: false,
            englishVoiceAvailable: false
        };

        if (!this.isSupported) {
            return results;
        }

        // Test synthesis
        results.synthesisSupported = true;

        // Test microphone permission
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            results.microphonePermission = true;
            stream.getTracks().forEach(track => track.stop());
        } catch (error) {
            results.microphonePermission = false;
        }

        // Test recognition
        try {
            this.initializeRecognition();
            results.recognitionSupported = true;
        } catch (error) {
            results.recognitionSupported = false;
        }

        // Check available voices
        const voices = this.getAvailableVoices();
        results.voicesAvailable = voices.length;
        results.hindiVoiceAvailable = voices.some(v => v.lang.startsWith('hi'));
        results.englishVoiceAvailable = voices.some(v => v.lang.startsWith('en'));

        return results;
    }

    /**
     * Cleanup resources
     */
    cleanup() {
        this.stopRecording();
        this.stopSpeaking();

        if (this.recognition) {
            this.recognition = null;
        }

        console.log('🎤 Speech Manager cleaned up');
    }
}

// Create global speech manager instance
window.speechManager = new SpeechManager();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SpeechManager;
}