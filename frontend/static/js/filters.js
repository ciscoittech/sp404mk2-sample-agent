// Filter functionality for HTMX
document.addEventListener('DOMContentLoaded', function() {
    // Intercept HTMX requests to clean up empty parameters
    document.body.addEventListener('htmx:configRequest', function(evt) {
        // Clean up empty parameters from the request
        const params = evt.detail.parameters;
        
        // Remove empty BPM values
        if (params['bpm-min'] === '') {
            delete params['bpm-min'];
        }
        if (params['bpm-max'] === '') {
            delete params['bpm-max'];
        }
        
        // Remove empty search
        if (params['search'] === '') {
            delete params['search'];
        }
        
        // Remove empty genre
        if (params['genre'] === '') {
            delete params['genre'];
        }
    });
});