/**
 * Internationalization (i18n) Configuration
 * Bilingual support for Hindi and English languages
 */

// Language translations
const translations = {
    en: null, // Will be loaded from en.json
    hi: null  // Will be loaded from hi.json
};

// Current language
let currentLanguage = 'en';

// Initialize i18n
class I18nManager {
    constructor() {
        this.currentLanguage = localStorage.getItem('cropgpt_language') || 'en';
        this.translations = {};
        this.isReady = false;
    }

    async init() {
        try {
            // Load language files
            await this.loadTranslations('en');
            await this.loadTranslations('hi');

            // Detect browser language
            if (!localStorage.getItem('cropgpt_language')) {
                const browserLang = this.detectBrowserLanguage();
                this.currentLanguage = browserLang;
                localStorage.setItem('cropgpt_language', browserLang);
            }

            // Apply language
            this.setLanguage(this.currentLanguage);
            this.isReady = true;

            // Show content
            document.body.classList.add('i18n-ready');
            document.getElementById('loading-screen').style.display = 'none';

            // Setup language toggle buttons
            this.setupLanguageToggle();

            console.log(`✅ i18n initialized with language: ${this.currentLanguage}`);
        } catch (error) {
            console.error('❌ Failed to initialize i18n:', error);
            // Fallback to English
            this.setLanguage('en');
            document.body.classList.add('i18n-ready');
            document.getElementById('loading-screen').style.display = 'none';
        }
    }

    async loadTranslations(lang) {
        try {
            const response = await fetch(`/static/locales/${lang}.json`);
            if (!response.ok) {
                throw new Error(`Failed to load ${lang} translations`);
            }
            this.translations[lang] = await response.json();
        } catch (error) {
            console.error(`Failed to load ${lang} translations:`, error);
            // Fallback: create empty translations object
            this.translations[lang] = {};
        }
    }

    detectBrowserLanguage() {
        const browserLang = navigator.language || navigator.userLanguage;

        // Check if browser language is Hindi
        if (browserLang.startsWith('hi')) {
            return 'hi';
        }

        // Default to English
        return 'en';
    }

    setLanguage(lang) {
        if (!this.translations[lang]) {
            console.warn(`Translations for ${lang} not available, falling back to English`);
            lang = 'en';
        }

        this.currentLanguage = lang;
        localStorage.setItem('cropgpt_language', lang);

        // Update HTML lang attribute
        document.documentElement.lang = lang;

        // Update language toggle buttons
        this.updateLanguageToggle();

        // Update all translatable elements
        this.updatePageLanguage();

        // Update number formatting
        this.updateNumberFormatting();

        // Update date formatting
        this.updateDateFormatting();

        console.log(`🌐 Language changed to: ${lang}`);
    }

    t(key, params = {}) {
        if (!this.translations[this.currentLanguage]) {
            console.warn(`Translations not loaded for ${this.currentLanguage}`);
            return key;
        }

        // Get translation using dot notation
        const translation = this.getNestedValue(this.translations[this.currentLanguage], key);

        if (!translation) {
            // Fallback to English if key not found in current language
            if (this.currentLanguage !== 'en') {
                const englishTranslation = this.getNestedValue(this.translations['en'], key);
                if (englishTranslation) {
                    return englishTranslation;
                }
            }

            console.warn(`Translation not found: ${key}`);
            return key;
        }

        // Replace parameters in translation
        return this.replaceParams(translation, params);
    }

    getNestedValue(obj, path) {
        return path.split('.').reduce((current, key) => {
            return current && current[key] !== undefined ? current[key] : null;
        }, obj);
    }

    replaceParams(text, params) {
        if (typeof text !== 'string') return text;

        return text.replace(/\{\{(\w+)\}\}/g, (match, key) => {
            return params[key] !== undefined ? params[key] : match;
        });
    }

    updatePageLanguage() {
        // Update all elements with data-i18n attribute
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            const translation = this.t(key);

            if (element.tagName === 'INPUT' && element.type === 'placeholder') {
                element.placeholder = translation;
            } else if (element.tagName === 'INPUT' && element.type === 'submit') {
                element.value = translation;
            } else {
                element.textContent = translation;
            }
        });

        // Update page title
        const titleElement = document.querySelector('title[data-i18n]');
        if (titleElement) {
            const titleKey = titleElement.getAttribute('data-i18n');
            document.title = this.t(titleKey);
        }

        // Update meta description
        const metaDescription = document.querySelector('meta[data-i18n]');
        if (metaDescription) {
            const descKey = metaDescription.getAttribute('data-i18n');
            metaDescription.content = this.t(descKey);
        }
    }

    updateLanguageToggle() {
        // Update toggle button states
        const enButton = document.getElementById('lang-en');
        const hiButton = document.getElementById('lang-hi');

        if (enButton && hiButton) {
            if (this.currentLanguage === 'en') {
                enButton.classList.add('bg-blue-600', 'text-white');
                enButton.classList.remove('bg-gray-200', 'text-gray-700');
                hiButton.classList.add('bg-gray-200', 'text-gray-700');
                hiButton.classList.remove('bg-blue-600', 'text-white');
            } else {
                hiButton.classList.add('bg-blue-600', 'text-white');
                hiButton.classList.remove('bg-gray-200', 'text-gray-700');
                enButton.classList.add('bg-gray-200', 'text-gray-700');
                enButton.classList.remove('bg-blue-600', 'text-white');
            }
        }
    }

    setupLanguageToggle() {
        const enButton = document.getElementById('lang-en');
        const hiButton = document.getElementById('lang-hi');

        if (enButton) {
            enButton.addEventListener('click', () => {
                this.setLanguage('en');
            });
        }

        if (hiButton) {
            hiButton.addEventListener('click', () => {
                this.setLanguage('hi');
            });
        }
    }

    updateNumberFormatting() {
        // Format numbers based on language
        document.querySelectorAll('[data-format-number]').forEach(element => {
            const number = parseFloat(element.getAttribute('data-number'));
            if (!isNaN(number)) {
                element.textContent = this.formatNumber(number);
            }
        });
    }

    updateDateFormatting() {
        // Format dates based on language
        document.querySelectorAll('[data-format-date]').forEach(element => {
            const dateString = element.getAttribute('data-date');
            if (dateString) {
                element.textContent = this.formatDate(dateString);
            }
        });
    }

    formatNumber(number) {
        if (this.currentLanguage === 'hi') {
            // Use Hindi numbering system
            return number.toLocaleString('hi-IN');
        } else {
            return number.toLocaleString('en-IN');
        }
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        if (this.currentLanguage === 'hi') {
            return date.toLocaleDateString('hi-IN', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        } else {
            return date.toLocaleDateString('en-IN', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        }
    }

    getCurrentLanguage() {
        return this.currentLanguage;
    }

    isHindi() {
        return this.currentLanguage === 'hi';
    }

    isEnglish() {
        return this.currentLanguage === 'en';
    }
}

// Global i18n instance
window.i18n = new I18nManager();

// Helper function for translations
window.t = (key, params = {}) => {
    return window.i18n.t(key, params);
};

// Initialize i18n when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.i18n.init();
});