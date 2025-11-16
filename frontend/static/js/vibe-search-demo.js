/**
 * Vibe Search Demo JavaScript
 *
 * This file provides mock data and demo functionality for the Vibe Search UI
 * while the backend API is being developed.
 *
 * Remove this file once the real /api/v1/search/vibe endpoint is implemented.
 */

// Mock sample data for demo purposes
const mockSamples = [
    {
        id: 1,
        title: "Dark Moody Piano Loop",
        bpm: 85,
        musical_key: "Am",
        genre: "hip-hop",
        sample_type: "loop",
        file_url: "/static/audio/demo/sample1.mp3",
        vibe_analysis: {
            tags: ["dark", "moody", "piano", "atmospheric"],
            energy_level: 45,
            danceability: 30,
            mood_primary: "Dark",
            mood_emoji: "🌙"
        },
        similarity: 92
    },
    {
        id: 2,
        title: "Energetic Trap Drums",
        bpm: 140,
        musical_key: "C",
        genre: "trap",
        sample_type: "loop",
        file_url: "/static/audio/demo/sample2.mp3",
        vibe_analysis: {
            tags: ["energetic", "trap", "drums", "hard-hitting"],
            energy_level: 85,
            danceability: 75,
            mood_primary: "Energetic",
            mood_emoji: "⚡"
        },
        similarity: 88
    },
    {
        id: 3,
        title: "Chill Jazzy Rhodes",
        bpm: 95,
        musical_key: "Dm7",
        genre: "jazz",
        sample_type: "loop",
        file_url: "/static/audio/demo/sample3.mp3",
        vibe_analysis: {
            tags: ["chill", "jazz", "rhodes", "smooth"],
            energy_level: 35,
            danceability: 40,
            mood_primary: "Chill",
            mood_emoji: "🌊"
        },
        similarity: 85
    },
    {
        id: 4,
        title: "Aggressive 808 Bass",
        bpm: 128,
        musical_key: "G",
        genre: "trap",
        sample_type: "oneshot",
        file_url: "/static/audio/demo/sample4.mp3",
        vibe_analysis: {
            tags: ["aggressive", "808", "bass", "heavy"],
            energy_level: 90,
            danceability: 60,
            mood_primary: "Aggressive",
            mood_emoji: "🔥"
        },
        similarity: 82
    },
    {
        id: 5,
        title: "Vintage Soul Sample",
        bpm: 110,
        musical_key: "F",
        genre: "soul",
        sample_type: "loop",
        file_url: "/static/audio/demo/sample5.mp3",
        vibe_analysis: {
            tags: ["vintage", "soul", "warm", "nostalgic"],
            energy_level: 55,
            danceability: 50,
            mood_primary: "Warm",
            mood_emoji: "☀️"
        },
        similarity: 78
    },
    {
        id: 6,
        title: "Ambient Atmospheric Pad",
        bpm: 72,
        musical_key: "Em",
        genre: "electronic",
        sample_type: "loop",
        file_url: "/static/audio/demo/sample6.mp3",
        vibe_analysis: {
            tags: ["ambient", "atmospheric", "pad", "ethereal"],
            energy_level: 25,
            danceability: 20,
            mood_primary: "Atmospheric",
            mood_emoji: "🌫️"
        },
        similarity: 75
    }
];

/**
 * Generate sample card HTML
 */
function generateSampleCard(sample) {
    const tagBadges = sample.vibe_analysis.tags
        .map(tag => `<span class="badge badge-sm badge-ghost">${tag}</span>`)
        .join('');

    return `
        <div class="card sample-card bg-base-100 shadow-xl hover:shadow-2xl transition-all duration-200 relative"
             x-data="vibeSampleCard(${sample.id}, '${sample.title}', ${sample.bpm}, '${sample.musical_key}', '${sample.genre}', '${sample.file_url}', ${sample.similarity})">

            <!-- Similarity Badge -->
            <div class="badge badge-primary absolute top-3 right-3 z-10 gap-1 shadow-lg">
                <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                </svg>
                <span>${sample.similarity}% match</span>
            </div>

            <!-- Waveform Preview -->
            <figure class="bg-base-200 h-32 relative overflow-hidden">
                <div class="waveform-container absolute inset-0 flex items-center justify-center">
                    <svg class="w-full h-16 text-primary/40" viewBox="0 0 200 40" preserveAspectRatio="none">
                        <path d="M0 20 L10 15 L20 25 L30 10 L40 30 L50 15 L60 25 L70 12 L80 28 L90 18 L100 22 L110 14 L120 26 L130 16 L140 24 L150 18 L160 22 L170 20 L180 25 L190 15 L200 20"
                              stroke="currentColor" stroke-width="2" fill="none" opacity="0.7"/>
                    </svg>
                </div>
            </figure>

            <div class="card-body p-4">
                <!-- Title -->
                <h3 class="card-title text-base line-clamp-2">${sample.title}</h3>

                <!-- Musical Properties -->
                <div class="flex gap-2 text-sm flex-wrap">
                    <span class="badge badge-sm">${sample.bpm} BPM</span>
                    <span class="badge badge-sm">${sample.musical_key}</span>
                    <span class="badge badge-sm capitalize">${sample.genre}</span>
                    <span class="badge badge-sm capitalize">${sample.sample_type}</span>
                </div>

                <!-- Vibe Tags -->
                <div class="flex gap-1 flex-wrap mt-2">
                    ${tagBadges}
                </div>

                <!-- Energy & Danceability -->
                <div class="space-y-2 mt-2">
                    <div class="flex items-center gap-2">
                        <span class="text-xs text-base-content/70 w-16">Energy</span>
                        <progress class="progress progress-primary w-full h-2" value="${sample.vibe_analysis.energy_level}" max="100"></progress>
                        <span class="text-xs font-semibold w-8">${sample.vibe_analysis.energy_level}%</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="text-xs text-base-content/70 w-16">Dance</span>
                        <progress class="progress progress-accent w-full h-2" value="${sample.vibe_analysis.danceability}" max="100"></progress>
                        <span class="text-xs font-semibold w-8">${sample.vibe_analysis.danceability}%</span>
                    </div>
                </div>

                <!-- Mood -->
                <div class="flex items-center gap-2 mt-2">
                    <span class="text-xs text-base-content/70">Mood:</span>
                    <span class="text-sm">${sample.vibe_analysis.mood_primary}</span>
                    <span>${sample.vibe_analysis.mood_emoji}</span>
                </div>

                <!-- Audio Player -->
                <div class="mt-3 bg-base-200 rounded-lg p-2" x-data="audioPlayer('${sample.file_url}')">
                    <div class="flex items-center gap-2">
                        <button @click="togglePlay()" class="btn btn-circle btn-sm btn-primary">
                            <svg x-show="!playing" class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z"/>
                            </svg>
                            <svg x-show="playing" class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd"/>
                            </svg>
                        </button>
                        <div class="flex-1">
                            <input type="range" :value="currentTime" :max="duration" @input="seek($event.target.value)" class="range range-xs range-primary" step="0.1">
                        </div>
                        <span class="text-xs font-mono" x-text="formatTime(currentTime)">0:00</span>
                        <span class="text-xs text-base-content/50">/</span>
                        <span class="text-xs font-mono text-base-content/70" x-text="formatTime(duration)">0:00</span>
                    </div>
                    <audio x-ref="audio" src="${sample.file_url}" @timeupdate="currentTime = $refs.audio.currentTime" @loadedmetadata="duration = $refs.audio.duration" @ended="playing = false" preload="metadata"></audio>
                </div>

                <!-- Actions -->
                <div class="card-actions justify-end mt-4 gap-2 flex-wrap">
                    <button @click="findSimilar()" class="btn btn-sm btn-ghost gap-1">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4"/>
                        </svg>
                        Similar
                    </button>
                    <button @click="addToKit()" class="btn btn-sm btn-primary gap-1">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
                        </svg>
                        Add to Kit
                    </button>
                    <a href="${sample.file_url}" download class="btn btn-sm btn-accent gap-1">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
                        </svg>
                        Download
                    </a>
                </div>
            </div>
        </div>
    `;
}

/**
 * Calculate result statistics
 */
function calculateStats(samples) {
    const avgSimilarity = samples.reduce((sum, s) => sum + s.similarity, 0) / samples.length;
    const bpms = samples.map(s => s.bpm);
    const bpmMin = Math.min(...bpms);
    const bpmMax = Math.max(...bpms);

    const genreCounts = {};
    samples.forEach(s => {
        genreCounts[s.genre] = (genreCounts[s.genre] || 0) + 1;
    });
    const topGenre = Object.keys(genreCounts).reduce((a, b) =>
        genreCounts[a] > genreCounts[b] ? a : b
    );

    return {
        count: samples.length,
        avgSimilarity: Math.round(avgSimilarity),
        bpmRange: `${bpmMin}-${bpmMax}`,
        topGenre: topGenre
    };
}

/**
 * Update results display
 */
function displayDemoResults(samples) {
    const resultsContainer = document.getElementById('search-results');
    if (!resultsContainer) return;

    // Generate cards HTML
    const cardsHtml = samples.map(sample => generateSampleCard(sample)).join('');
    resultsContainer.innerHTML = cardsHtml;

    // Update stats
    const stats = calculateStats(samples);
    document.getElementById('result-count').textContent = stats.count;
    document.getElementById('avg-similarity').textContent = `${stats.avgSimilarity}%`;
    document.getElementById('bpm-range').textContent = stats.bpmRange;
    document.getElementById('top-genre').textContent = stats.topGenre;

    // Show stats and sort options
    document.getElementById('results-stats')?.classList.remove('hidden');
    document.getElementById('sort-options')?.classList.remove('hidden');
}

/**
 * Demo: Intercept HTMX requests and return mock data
 */
function enableDemoMode() {
    console.log('🎵 Vibe Search Demo Mode Enabled');

    // Intercept HTMX requests
    document.body.addEventListener('htmx:configRequest', function(event) {
        if (event.detail.path === '/api/v1/search/vibe') {
            event.preventDefault();

            // Simulate loading delay
            setTimeout(() => {
                displayDemoResults(mockSamples);
            }, 1000);
        }
    });
}

// Initialize demo mode when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', enableDemoMode);
} else {
    enableDemoMode();
}

/**
 * Export for use in vibe-search page
 */
window.VibeSearchDemo = {
    samples: mockSamples,
    displayResults: displayDemoResults,
    calculateStats: calculateStats
};
