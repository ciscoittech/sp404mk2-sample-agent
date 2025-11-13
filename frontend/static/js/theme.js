/**
 * Theme System for SP404MK2 Sample Manager
 * Handles theme switching, persistence, and system preference detection
 */

// Available themes grouped by light/dark
const THEMES = {
    light: ['light', 'lofi'],
    dark: ['dark', 'synthwave', 'dracula', 'cyberpunk', 'business', 'forest']
};

// Flat list of all available themes
const ALL_THEMES = ['light', 'dark', 'synthwave', 'dracula', 'cyberpunk', 'business', 'lofi', 'forest'];

// Storage key for theme preference
const THEME_STORAGE_KEY = 'sp404mk2-theme';

/**
 * Initialize theme system on page load
 * Priority: localStorage > system preference > default (dark)
 */
function initTheme() {
    const savedTheme = localStorage.getItem(THEME_STORAGE_KEY);
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const defaultTheme = savedTheme || (prefersDark ? 'dark' : 'light');

    setTheme(defaultTheme);
}

/**
 * Apply theme to document
 * @param {string} themeName - Name of theme to apply
 */
function setTheme(themeName) {
    if (!ALL_THEMES.includes(themeName)) {
        console.warn(`Invalid theme: ${themeName}. Falling back to 'dark'.`);
        themeName = 'dark';
    }

    // Update HTML data-theme attribute
    document.documentElement.setAttribute('data-theme', themeName);

    // Save to localStorage
    localStorage.setItem(THEME_STORAGE_KEY, themeName);

    // Dispatch custom event for other components to react
    window.dispatchEvent(new CustomEvent('themeChanged', {
        detail: { theme: themeName }
    }));

    console.log(`Theme changed to: ${themeName}`);
}

/**
 * Get currently active theme
 * @returns {string} Current theme name
 */
function getCurrentTheme() {
    return document.documentElement.getAttribute('data-theme') || 'dark';
}

/**
 * Check if current theme is dark
 * @returns {boolean} True if current theme is dark
 */
function isDarkTheme() {
    const currentTheme = getCurrentTheme();
    return THEMES.dark.includes(currentTheme);
}

/**
 * Toggle between light and dark mode
 * Switches to default theme of opposite mode
 */
function toggleDarkMode() {
    const current = getCurrentTheme();
    const isLight = THEMES.light.includes(current);
    const newTheme = isLight ? 'dark' : 'light';
    setTheme(newTheme);
}

/**
 * Get next theme in the list (for keyboard shortcuts)
 * @returns {string} Next theme name
 */
function getNextTheme() {
    const current = getCurrentTheme();
    const currentIndex = ALL_THEMES.indexOf(current);
    const nextIndex = (currentIndex + 1) % ALL_THEMES.length;
    return ALL_THEMES[nextIndex];
}

/**
 * Cycle to next theme
 */
function cycleTheme() {
    const nextTheme = getNextTheme();
    setTheme(nextTheme);
}

// Initialize theme when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTheme);
} else {
    initTheme();
}

// Listen for system theme preference changes
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    // Only auto-switch if user hasn't manually selected a theme
    if (!localStorage.getItem(THEME_STORAGE_KEY)) {
        setTheme(e.matches ? 'dark' : 'light');
    }
});

// Keyboard shortcut: Ctrl+Shift+T to cycle themes
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.shiftKey && e.key === 'T') {
        e.preventDefault();
        cycleTheme();

        // Show toast notification
        showThemeToast(`Theme: ${getCurrentTheme()}`);
    }
});

/**
 * Show brief toast notification for theme change
 * @param {string} message - Message to display
 */
function showThemeToast(message) {
    const existingToast = document.getElementById('theme-toast');
    if (existingToast) {
        existingToast.remove();
    }

    const toast = document.createElement('div');
    toast.id = 'theme-toast';
    toast.className = 'toast toast-top toast-end z-50';
    toast.innerHTML = `
        <div class="alert alert-info shadow-lg">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01"/>
            </svg>
            <span>${message}</span>
        </div>
    `;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 2000);
}

// Export functions for use in other scripts (if needed)
if (typeof window !== 'undefined') {
    window.themeSystem = {
        setTheme,
        getCurrentTheme,
        isDarkTheme,
        toggleDarkMode,
        cycleTheme,
        THEMES,
        ALL_THEMES
    };
}
