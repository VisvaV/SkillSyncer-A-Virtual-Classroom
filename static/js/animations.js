// animations.js - Handles all animation effects

document.addEventListener('DOMContentLoaded', function () {
    // Loading Bar Animation
    const loadingBar = document.getElementById('loading-bar');
    const progressBarInner = document.querySelector('.progress-bar-inner');

    // Simulate loading and hide after page load
    function hideLoadingBar() {
        let width = 0;
        const interval = setInterval(() => {
            if (width >= 100) {
                clearInterval(interval);
                loadingBar.classList.add('animate__fadeOut');
                setTimeout(() => {
                    loadingBar.style.display = 'none';
                }, 500); // Match fadeOut duration
            } else {
                width += 1;
                progressBarInner.style.width = `${width}%`;
            }
        }, 20);
    }

    // Hide loading bar after a short delay to ensure content loads
    window.addEventListener('load', hideLoadingBar);

    // Glow Effect on Hover for Interactive Elements
    const glowElements = document.querySelectorAll('.glow-on-hover, .card, .btn-primary, .btn-secondary, .nav-link');
    glowElements.forEach(element => {
        element.addEventListener('mouseenter', () => {
            element.style.boxShadow = '0 0 20px #0FFCBE, 0 0 30px #106EBE';
            element.style.transition = 'box-shadow 0.3s ease';
        });
        element.addEventListener('mouseleave', () => {
            element.style.boxShadow = 'none';
        });
    });

    // Card Flip Animation on Click (Optional Enhancement)
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('click', () => {
            card.classList.add('animate__flipInY');
            setTimeout(() => {
                card.classList.remove('animate__flipInY');
            }, 1000); // Match animation duration
        });
    });

    // Smooth Scroll Animation (if needed for future internal links)
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
});