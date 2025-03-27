// base.js

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide flash messages after 5 seconds
    setTimeout(function() {
        const flashes = document.querySelectorAll('.flashes');
        flashes.forEach(flash => {
            flash.style.transition = 'opacity 0.5s ease-in-out';
            flash.style.opacity = '0';
            setTimeout(() => flash.remove(), 500);
        });
    }, 5000);
});
