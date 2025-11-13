/**
 * Global Alpine.js Components for SP404MK2 Sample Manager
 * These components are available on all pages
 */

/**
 * Theme Switcher Component
 * Manages theme selection UI and persistence
 */
function themeSwitcher() {
    return {
        currentTheme: 'dark',
        themes: [
            { name: 'light', label: 'Light', icon: '☀️', description: 'Clean light mode' },
            { name: 'dark', label: 'Dark', icon: '🌙', description: 'Professional dark' },
            { name: 'synthwave', label: 'Synthwave', icon: '🌆', description: 'Retro 80s neon' },
            { name: 'dracula', label: 'Dracula', icon: '🧛', description: 'Popular dev theme' },
            { name: 'cyberpunk', label: 'Cyberpunk', icon: '🤖', description: 'Futuristic high contrast' },
            { name: 'business', label: 'Business', icon: '💼', description: 'Sleek corporate' },
            { name: 'lofi', label: 'Lo-fi', icon: '🎵', description: 'Muted pastels' },
            { name: 'forest', label: 'Forest', icon: '🌲', description: 'Natural green tones' }
        ],

        init() {
            // Get initial theme
            this.currentTheme = getCurrentTheme();

            // Listen for theme changes from other sources
            window.addEventListener('themeChanged', (e) => {
                this.currentTheme = e.detail.theme;
            });
        },

        selectTheme(themeName) {
            setTheme(themeName);
            this.currentTheme = themeName;

            // Close dropdown after selection (DaisyUI specific)
            document.activeElement.blur();
        },

        isDark() {
            return !['light', 'lofi'].includes(this.currentTheme);
        },

        toggleDarkMode() {
            const isLight = ['light', 'lofi'].includes(this.currentTheme);
            const newTheme = isLight ? 'dark' : 'light';
            this.selectTheme(newTheme);
        }
    };
}

/**
 * Sample Audio Player Component
 * Manages playback of audio samples with waveform visualization
 * @param {string} audioUrl - URL of audio file to play
 */
function samplePlayer(audioUrl) {
    return {
        audio: null,
        playing: false,
        currentTime: 0,
        duration: 0,
        loading: true,

        init() {
            this.audio = new Audio(audioUrl);

            // Event listeners
            this.audio.addEventListener('loadedmetadata', () => {
                this.duration = this.audio.duration;
                this.loading = false;
            });

            this.audio.addEventListener('timeupdate', () => {
                this.currentTime = this.audio.currentTime;
            });

            this.audio.addEventListener('ended', () => {
                this.playing = false;
                this.currentTime = 0;
            });

            this.audio.addEventListener('error', (e) => {
                console.error('Audio loading error:', e);
                this.loading = false;
            });
        },

        togglePlay() {
            if (this.playing) {
                this.audio.pause();
            } else {
                // Pause all other playing samples
                document.querySelectorAll('audio').forEach(a => {
                    if (a !== this.audio) {
                        a.pause();
                    }
                });

                this.audio.play();
            }
            this.playing = !this.playing;
        },

        seek(event) {
            const progressBar = event.currentTarget;
            const clickPosition = event.offsetX / progressBar.offsetWidth;
            this.audio.currentTime = clickPosition * this.duration;
        },

        formatTime(seconds) {
            if (!seconds || isNaN(seconds)) return '0:00';
            const mins = Math.floor(seconds / 60);
            const secs = Math.floor(seconds % 60);
            return `${mins}:${secs.toString().padStart(2, '0')}`;
        },

        getProgress() {
            if (!this.duration) return 0;
            return (this.currentTime / this.duration) * 100;
        }
    };
}

/**
 * Sample Filter Component
 * Manages search and filter state for sample library
 */
function sampleFilters() {
    return {
        search: '',
        genre: '',
        bpmMin: '',
        bpmMax: '',

        init() {
            // Load filter state from URL params if present
            const params = new URLSearchParams(window.location.search);
            this.search = params.get('search') || '';
            this.genre = params.get('genre') || '';
            this.bpmMin = params.get('bpm_min') || '';
            this.bpmMax = params.get('bpm_max') || '';
        },

        clearFilters() {
            this.search = '';
            this.genre = '';
            this.bpmMin = '';
            this.bpmMax = '';

            // Trigger HTMX reload
            htmx.trigger('#sample-grid', 'load');
        },

        hasActiveFilters() {
            return this.search || this.genre || this.bpmMin || this.bpmMax;
        }
    };
}

/**
 * Mood Visualization Component
 * Renders animated canvas visualization for vibe analysis
 */
function moodViz() {
    return {
        ctx: null,
        canvas: null,
        animationId: null,
        particles: [],
        mood: 'neutral',

        init() {
            this.canvas = this.$refs.canvas;
            if (!this.canvas) return;

            this.ctx = this.canvas.getContext('2d');
            this.canvas.width = this.canvas.offsetWidth;
            this.canvas.height = this.canvas.offsetHeight;

            this.initParticles();
            this.animate();
        },

        initParticles() {
            this.particles = [];
            for (let i = 0; i < 30; i++) {
                this.particles.push({
                    x: Math.random() * this.canvas.width,
                    y: Math.random() * this.canvas.height,
                    radius: Math.random() * 3 + 1,
                    speedX: (Math.random() - 0.5) * 0.5,
                    speedY: (Math.random() - 0.5) * 0.5,
                    hue: Math.random() * 360
                });
            }
        },

        animate() {
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

            // Draw and update particles
            this.particles.forEach(particle => {
                // Draw particle
                this.ctx.beginPath();
                this.ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
                this.ctx.fillStyle = `hsla(${particle.hue}, 70%, 60%, 0.6)`;
                this.ctx.fill();

                // Update position
                particle.x += particle.speedX;
                particle.y += particle.speedY;

                // Wrap around edges
                if (particle.x < 0) particle.x = this.canvas.width;
                if (particle.x > this.canvas.width) particle.x = 0;
                if (particle.y < 0) particle.y = this.canvas.height;
                if (particle.y > this.canvas.height) particle.y = 0;
            });

            this.animationId = requestAnimationFrame(() => this.animate());
        },

        setMood(newMood) {
            this.mood = newMood;
            // Adjust particle colors based on mood
            const moodHues = {
                'energetic': 0,    // Red
                'calm': 200,       // Blue
                'dark': 280,       // Purple
                'uplifting': 60,   // Yellow
                'melancholic': 240 // Deep blue
            };

            const baseHue = moodHues[newMood] || 180;
            this.particles.forEach(particle => {
                particle.hue = baseHue + (Math.random() - 0.5) * 60;
            });
        },

        destroy() {
            if (this.animationId) {
                cancelAnimationFrame(this.animationId);
            }
        }
    };
}

/**
 * Kit Builder Component
 * Manages SP-404 style pad grid for kit building
 */
function kitBuilder() {
    return {
        pads: Array(16).fill(null), // 16 pads like SP-404MK2
        selectedPad: null,
        draggedSample: null,

        assignSample(sample, padIndex) {
            this.pads[padIndex] = sample;
            this.savePads();
        },

        clearPad(padIndex) {
            this.pads[padIndex] = null;
            this.savePads();
        },

        selectPad(padIndex) {
            this.selectedPad = padIndex;
        },

        handleDrop(event, padIndex) {
            event.preventDefault();
            const sampleData = event.dataTransfer.getData('application/json');
            if (sampleData) {
                const sample = JSON.parse(sampleData);
                this.assignSample(sample, padIndex);
            }
        },

        savePads() {
            // Save to localStorage or backend
            localStorage.setItem('sp404-kit-pads', JSON.stringify(this.pads));
        },

        loadPads() {
            const saved = localStorage.getItem('sp404-kit-pads');
            if (saved) {
                this.pads = JSON.parse(saved);
            }
        },

        init() {
            this.loadPads();
        }
    };
}

/**
 * Toast Notification Helper
 * Shows temporary notification messages
 */
function showToast(message, type = 'info', duration = 3000) {
    const toastId = 'global-toast-' + Date.now();
    const alertClasses = {
        'info': 'alert-info',
        'success': 'alert-success',
        'warning': 'alert-warning',
        'error': 'alert-error'
    };

    const toast = document.createElement('div');
    toast.id = toastId;
    toast.className = 'toast toast-top toast-end z-50';
    toast.innerHTML = `
        <div class="alert ${alertClasses[type] || 'alert-info'} shadow-lg">
            <span>${message}</span>
        </div>
    `;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, duration);
}

// Make showToast globally available
window.showToast = showToast;

/**
 * HTMX Event Handlers
 * Global handlers for HTMX events
 */
document.body.addEventListener('htmx:afterRequest', (evt) => {
    const xhr = evt.detail.xhr;

    if (xhr.status >= 200 && xhr.status < 300) {
        // Success - could show toast if needed
    } else if (xhr.status === 401) {
        // Unauthorized - redirect to login
        window.location.href = '/login.html';
    } else if (xhr.status >= 400) {
        // Error - show toast
        showToast('Request failed. Please try again.', 'error');
    }
});

document.body.addEventListener('htmx:responseError', (evt) => {
    console.error('HTMX response error:', evt.detail);
    showToast('Network error. Please check your connection.', 'error');
});

// Handle HTMX load events for analytics or logging
document.body.addEventListener('htmx:load', (evt) => {
    console.log('HTMX content loaded:', evt.detail.elt);
});
