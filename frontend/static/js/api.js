/**
 * API Client
 * HTTP client for communicating with CropGPT backend APIs
 */

class ApiClient {
    constructor() {
        this.baseURL = this.getBaseURL();
        this.defaultHeaders = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };
    }

    /**
     * Get base URL for API calls
     */
    getBaseURL() {
        // In development, use the current host with port 8000
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return `${window.location.protocol}//${window.location.hostname}:8000`;
        }
        // In production, use the same host
        return `${window.location.protocol}//${window.location.hostname}`;
    }

    /**
     * Get authorization headers
     */
    getAuthHeaders() {
        const token = localStorage.getItem('cropgpt_token');
        return token ? { 'Authorization': `Bearer ${token}` } : {};
    }

    /**
     * Make HTTP request
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}/api${endpoint}`;
        const config = {
            headers: {
                ...this.defaultHeaders,
                ...this.getAuthHeaders(),
                ...options.headers
            },
            ...options
        };

        try {
            console.log(`🌐 API Request: ${config.method || 'GET'} ${url}`);

            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new ApiError(data.message || 'Request failed', response.status, data);
            }

            console.log(`✅ API Response: ${config.method || 'GET'} ${url}`, data);
            return data;
        } catch (error) {
            console.error(`❌ API Error: ${config.method || 'GET'} ${url}`, error);
            throw error;
        }
    }

    /**
     * GET request
     */
    async get(endpoint, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;
        return this.request(url, { method: 'GET' });
    }

    /**
     * POST request
     */
    async post(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    /**
     * PUT request
     */
    async put(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    /**
     * DELETE request
     */
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }

    /**
     * Upload file
     */
    async upload(endpoint, file, additionalData = {}) {
        const formData = new FormData();
        formData.append('file', file);

        // Add additional form data
        Object.keys(additionalData).forEach(key => {
            formData.append(key, additionalData[key]);
        });

        return this.request(endpoint, {
            method: 'POST',
            body: formData,
            headers: {
                // Don't set Content-Type for FormData (browser sets it with boundary)
                ...this.getAuthHeaders()
            }
        });
    }
}

/**
 * Custom API Error class
 */
class ApiError extends Error {
    constructor(message, status, data = null) {
        super(message);
        this.name = 'ApiError';
        this.status = status;
        this.data = data;
    }
}

/**
 * API Service Classes
 */
class ChatService {
    constructor(apiClient) {
        this.api = apiClient;
    }

    async sendMessage(message, language = null, sessionId = null) {
        const data = {
            message,
            language: language || window.i18n.getCurrentLanguage(),
            session_id: sessionId || this.generateSessionId()
        };

        return this.api.post('/chat', data);
    }

    async getChatHistory(sessionId) {
        return this.api.get(`/chat/history/${sessionId}`);
    }

    generateSessionId() {
        return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
}

class PricesService {
    constructor(apiClient) {
        this.api = apiClient;
    }

    async getCurrentPrices(filters = {}) {
        const params = {
            language: window.i18n.getCurrentLanguage(),
            ...filters
        };

        return this.api.get('/prices/current', params);
    }

    async getPriceHistory(commodity, market, days = 30) {
        return this.api.get('/prices/history', {
            commodity,
            market,
            days,
            language: window.i18n.getCurrentLanguage()
        });
    }

    async getPricesComparison(commodity, date = null) {
        return this.api.get('/prices/comparison', {
            commodity,
            date: date || new Date().toISOString().split('T')[0],
            language: window.i18n.getCurrentLanguage()
        });
    }

    async createPriceAlert(alertData) {
        return this.api.post('/prices/alerts', alertData);
    }

    async getPriceAlerts() {
        return this.api.get('/prices/alerts');
    }

    async deletePriceAlert(alertId) {
        return this.api.delete(`/prices/alerts/${alertId}`);
    }
}

class WeatherService {
    constructor(apiClient) {
        this.api = apiClient;
    }

    async getCurrentWeather() {
        return this.api.get('/weather/current', {
            language: window.i18n.getCurrentLanguage()
        });
    }

    async getForecast() {
        return this.api.get('/weather/forecast', {
            language: window.i18n.getCurrentLanguage()
        });
    }

    async getWeatherAlerts() {
        return this.api.get('/weather/alerts', {
            language: window.i18n.getCurrentLanguage()
        });
    }
}

class SchemesService {
    constructor(apiClient) {
        this.api = apiClient;
    }

    async getAllSchemes(filters = {}) {
        return this.api.get('/schemes', {
            language: window.i18n.getCurrentLanguage(),
            ...filters
        });
    }

    async getScheme(schemeId) {
        return this.api.get(`/schemes/${schemeId}`, {
            language: window.i18n.getCurrentLanguage()
        });
    }

    async searchSchemes(query, filters = {}) {
        return this.api.get('/schemes/search', {
            query,
            language: window.i18n.getCurrentLanguage(),
            ...filters
        });
    }

    async applyForScheme(schemeId, applicationData) {
        return this.api.post('/schemes/apply', {
            scheme_id: schemeId,
            ...applicationData
        });
    }

    async getSchemeApplications() {
        return this.api.get('/schemes/applications');
    }

    async updateApplicationStatus(applicationId, status, notes = null) {
        return this.api.put(`/schemes/applications/${applicationId}`, {
            status,
            notes
        });
    }
}

class UserService {
    constructor(apiClient) {
        this.api = apiClient;
    }

    async createProfile(userData) {
        return this.api.post('/users', userData);
    }

    async getProfile() {
        return this.api.get('/users/me');
    }

    async updateProfile(userData) {
        return this.api.put('/users/me', userData);
    }

    async deleteProfile() {
        return this.api.delete('/users/me');
    }

    async updatePreferences(preferences) {
        return this.api.put('/users/preferences', preferences);
    }
}

// Create API client and service instances
const apiClient = new ApiClient();
const chatService = new ChatService(apiClient);
const pricesService = new PricesService(apiClient);
const weatherService = new WeatherService(apiClient);
const schemesService = new SchemesService(apiClient);
const userService = new UserService(apiClient);

// Global API access
window.api = {
    client: apiClient,
    chat: chatService,
    prices: pricesService,
    weather: weatherService,
    schemes: schemesService,
    user: userService,
    error: ApiError
};

// Health check function
window.checkApiHealth = async function() {
    try {
        const response = await apiClient.get('/health');
        return response.status === 'healthy';
    } catch (error) {
        console.error('API health check failed:', error);
        return false;
    }
};

// Initialize API health check
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(async () => {
        const isHealthy = await window.checkApiHealth();
        if (!isHealthy) {
            console.warn('⚠️ API server is not responding');
            // You might want to show a user-friendly message here
        }
    }, 2000);
});