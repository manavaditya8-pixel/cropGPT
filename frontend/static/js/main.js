/**
 * Main Application JavaScript
 * Core functionality for CropGPT farmer assistant web application
 */

// Application state
const AppState = {
    currentSection: 'home',
    isLoading: false,
    user: null,
    stats: {
        chatCount: 0,
        priceCount: 0,
        weatherTemp: '--',
        schemeCount: 0
    }
};

// DOM Content Loaded
document.addEventListener('DOMContentLoaded', async () => {
    try {
        console.log('🚀 Initializing CropGPT Application...');

        // Wait for i18n to be ready
        await waitForI18n();

        // Initialize application components
        initializeNavigation();
        initializeMobileMenu();
        initializeFeatureCards();
        loadDashboardData();

        // Hide loading screen
        setTimeout(() => {
            const loadingScreen = document.getElementById('loading-screen');
            if (loadingScreen) {
                loadingScreen.style.opacity = '0';
                setTimeout(() => {
                    loadingScreen.style.display = 'none';
                }, 300);
            }
        }, 1000);

        console.log('✅ CropGPT Application initialized successfully');
    } catch (error) {
        console.error('❌ Failed to initialize application:', error);
        showError('Application initialization failed. Please refresh the page.');
    }
});

/**
 * Wait for i18n to be ready
 */
function waitForI18n() {
    return new Promise((resolve) => {
        const checkI18n = () => {
            if (window.i18n && window.i18n.isReady) {
                resolve();
            } else {
                setTimeout(checkI18n, 100);
            }
        };
        checkI18n();
    });
}

/**
 * Initialize navigation functionality
 */
function initializeNavigation() {
    // Navigation links
    const navLinks = document.querySelectorAll('.nav-link, .mobile-nav-link');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href').substring(1);
            navigateToSection(targetId);
        });
    });

    // Handle browser back/forward buttons
    window.addEventListener('popstate', (e) => {
        if (e.state && e.state.section) {
            showSection(e.state.section);
        }
    });

    // Set initial section
    const hash = window.location.hash.substring(1) || 'home';
    showSection(hash);
}

/**
 * Initialize mobile menu
 */
function initializeMobileMenu() {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');

    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', () => {
            const isHidden = mobileMenu.classList.contains('hidden');

            if (isHidden) {
                mobileMenu.classList.remove('hidden');
                mobileMenuButton.innerHTML = '<i class="fas fa-times text-gray-700 text-xl"></i>';
            } else {
                mobileMenu.classList.add('hidden');
                mobileMenuButton.innerHTML = '<i class="fas fa-bars text-gray-700 text-xl"></i>';
            }
        });

        // Close mobile menu when clicking on a link
        const mobileNavLinks = mobileMenu.querySelectorAll('.mobile-nav-link');
        mobileNavLinks.forEach(link => {
            link.addEventListener('click', () => {
                mobileMenu.classList.add('hidden');
                mobileMenuButton.innerHTML = '<i class="fas fa-bars text-gray-700 text-xl"></i>';
            });
        });
    }
}

/**
 * Initialize feature cards
 */
function initializeFeatureCards() {
    const featureCards = document.querySelectorAll('.feature-card');

    featureCards.forEach(card => {
        card.addEventListener('click', () => {
            const targetSection = card.getAttribute('data-section');
            if (targetSection) {
                navigateToSection(targetSection);
            }
        });

        // Add hover effects
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-4px)';
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0)';
        });
    });
}

/**
 * Navigate to a specific section
 */
function navigateToSection(sectionId) {
    // Update URL
    history.pushState({ section: sectionId }, '', `#${sectionId}`);
    showSection(sectionId);
}

/**
 * Show a specific section
 */
function showSection(sectionId) {
    // Hide all sections
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => {
        section.classList.add('hidden');
    });

    // Show target section
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.remove('hidden');
        AppState.currentSection = sectionId;

        // Update active nav link
        updateActiveNavLink(sectionId);

        // Load section-specific data
        loadSectionData(sectionId);

        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    } else {
        console.warn(`Section ${sectionId} not found`);
        showSection('home');
    }
}

/**
 * Update active navigation link
 */
function updateActiveNavLink(sectionId) {
    const navLinks = document.querySelectorAll('.nav-link, .mobile-nav-link');

    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === `#${sectionId}`) {
            link.classList.add('text-green-600', 'font-semibold');
            link.classList.remove('text-gray-700');
        } else {
            link.classList.remove('text-green-600', 'font-semibold');
            link.classList.add('text-gray-700');
        }
    });
}

/**
 * Load section-specific data
 */
async function loadSectionData(sectionId) {
    switch (sectionId) {
        case 'home':
            await loadDashboardData();
            break;
        case 'chat':
            await loadChatData();
            break;
        case 'prices':
            await loadPricesData();
            break;
        case 'weather':
            await loadWeatherData();
            break;
        case 'schemes':
            await loadSchemesData();
            break;
        case 'about':
            await loadAboutData();
            break;
    }
}

/**
 * Load dashboard data
 */
async function loadDashboardData() {
    try {
        showLoading(true);

        // Simulate API calls (replace with actual API calls)
        const stats = await fetchDashboardStats();
        updateDashboardStats(stats);

        showLoading(false);
    } catch (error) {
        console.error('Failed to load dashboard data:', error);
        showError('Failed to load dashboard data');
        showLoading(false);
    }
}

/**
 * Fetch dashboard statistics
 */
async function fetchDashboardStats() {
    // Simulate API calls - replace with actual API endpoints
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve({
                chatCount: Math.floor(Math.random() * 100) + 50,
                priceCount: Math.floor(Math.random() * 20) + 10,
                weatherTemp: Math.floor(Math.random() * 10) + 25,
                schemeCount: Math.floor(Math.random() * 15) + 8
            });
        }, 1000);
    });
}

/**
 * Update dashboard statistics
 */
function updateDashboardStats(stats) {
    // Update chat count
    const chatCountElement = document.getElementById('chat-count');
    if (chatCountElement) {
        animateNumber(chatCountElement, 0, stats.chatCount, 1000);
    }

    // Update price count
    const priceCountElement = document.getElementById('price-count');
    if (priceCountElement) {
        animateNumber(priceCountElement, 0, stats.priceCount, 1000);
    }

    // Update weather temperature
    const weatherTempElement = document.getElementById('weather-temp');
    if (weatherTempElement) {
        weatherTempElement.textContent = `${stats.weatherTemp}°C`;
    }

    // Update scheme count
    const schemeCountElement = document.getElementById('scheme-count');
    if (schemeCountElement) {
        animateNumber(schemeCountElement, 0, stats.schemeCount, 1000);
    }

    AppState.stats = stats;
}

/**
 * Animate number counting
 */
function animateNumber(element, start, end, duration) {
    const startTime = performance.now();

    function updateNumber(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        const current = Math.floor(start + (end - start) * progress);
        element.textContent = current;

        if (progress < 1) {
            requestAnimationFrame(updateNumber);
        }
    }

    requestAnimationFrame(updateNumber);
}

/**
 * Load chat data (placeholder)
 */
async function loadChatData() {
    console.log('Loading chat data...');
    // TODO: Implement chat interface
}

/**
 * Load prices data (placeholder)
 */
async function loadPricesData() {
    console.log('Loading prices data...');
    // TODO: Implement prices dashboard
}

/**
 * Load weather data (placeholder)
 */
async function loadWeatherData() {
    console.log('Loading weather data...');
    // TODO: Implement weather forecast
}

/**
 * Load schemes data (placeholder)
 */
async function loadSchemesData() {
    console.log('Loading schemes data...');
    // TODO: Implement schemes portal
}

/**
 * Load about data (placeholder)
 */
async function loadAboutData() {
    console.log('Loading about data...');
    // TODO: Implement about page
}

/**
 * Show/hide loading state
 */
function showLoading(show) {
    AppState.isLoading = show;

    // You can add a global loading indicator here
    const loadingElements = document.querySelectorAll('.loading-indicator');
    loadingElements.forEach(element => {
        element.style.display = show ? 'block' : 'none';
    });
}

/**
 * Show error message
 */
function showError(message) {
    // Create error toast
    const errorToast = document.createElement('div');
    errorToast.className = 'fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg z-50';
    errorToast.innerHTML = `
        <div class="flex items-center">
            <i class="fas fa-exclamation-circle mr-2"></i>
            <span>${message}</span>
        </div>
    `;

    document.body.appendChild(errorToast);

    // Auto remove after 5 seconds
    setTimeout(() => {
        errorToast.remove();
    }, 5000);
}

/**
 * Show success message
 */
function showSuccess(message) {
    // Create success toast
    const successToast = document.createElement('div');
    successToast.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50';
    successToast.innerHTML = `
        <div class="flex items-center">
            <i class="fas fa-check-circle mr-2"></i>
            <span>${message}</span>
        </div>
    `;

    document.body.appendChild(successToast);

    // Auto remove after 3 seconds
    setTimeout(() => {
        successToast.remove();
    }, 3000);
}

/**
 * Format currency based on language
 */
function formatCurrency(amount) {
    if (window.i18n.isHindi()) {
        return `₹${amount.toLocaleString('hi-IN')}`;
    } else {
        return `₹${amount.toLocaleString('en-IN')}`;
    }
}

/**
 * Format date based on language
 */
function formatDate(dateString) {
    return window.i18n.formatDate(dateString);
}

/**
 * Debounce function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export for use in other modules
window.AppState = AppState;
window.showLoading = showLoading;
window.showError = showError;
window.showSuccess = showSuccess;
window.formatCurrency = formatCurrency;
window.formatDate = formatDate;
window.debounce = debounce;