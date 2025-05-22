// script.js - Main loader and initialization file

document.addEventListener('DOMContentLoaded', function () {
    // Initialize all modules
    console.log('Initializing SkillSyncer frontend enhancements...');

    // Load animations
    const animationsScript = document.createElement('script');
    animationsScript.src = '{{ url_for("static", filename="js/animations.js") }}';
    document.body.appendChild(animationsScript);

    // Load form utilities
    const formUtilsScript = document.createElement('script');
    formUtilsScript.src = '{{ url_for("static", filename="js/formUtils.js") }}';
    document.body.appendChild(formUtilsScript);

    // Load navigation effects
    const navigationScript = document.createElement('script');
    navigationScript.src = '{{ url_for("static", filename="js/navigation.js") }}';
    document.body.appendChild(navigationScript);

    // Preload images for smoother transitions
    const images = [
        '{{ url_for("static", filename="images/logo.png") }}',
        '{{ url_for("static", filename="images/favicon.ico") }}'
    ];
    images.forEach(src => {
        const img = new Image();
        img.src = src;
    });

    // Ensure page is fully loaded before removing loading state
    window.addEventListener('load', function () {
        console.log('Page fully loaded, enhancing UI...');
        document.body.classList.add('loaded');
    });
});

// Add loaded class to body after initialization
document.body.classList.add('animate__animated', 'animate__fadeIn');