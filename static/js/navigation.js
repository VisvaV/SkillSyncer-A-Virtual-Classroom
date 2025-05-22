
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const href = this.getAttribute('href');
            if (href && href !== '#') {
                link.classList.add('animate__pulse');
                setTimeout(() => {
                    link.classList.remove('animate__pulse');
                    window.location.href = href;
                }, 300);
            }
        });
    });


    const sidebar = document.querySelector('.sidebar');
    const navbarToggler = document.querySelector('.navbar-toggler');
    if (sidebar && navbarToggler) {
        navbarToggler.addEventListener('click', function () {
            sidebar.classList.toggle('active');
            if (sidebar.classList.contains('active')) {
                sidebar.style.transform = 'translateX(0)';
                sidebar.classList.add('animate__slideInLeft');
            } else {
                sidebar.classList.add('animate__slideOutLeft');
                setTimeout(() => {
                    sidebar.style.transform = 'translateX(-100%)';
                    sidebar.classList.remove('animate__slideOutLeft');
                }, 500);
            }
            setTimeout(() => {
                sidebar.classList.remove('animate__slideInLeft');
            }, 500); // Match slideInLeft duration
        });
    }

    // Navbar Glow Effect on Hover
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        navbar.addEventListener('mouseenter', () => {
            navbar.style.boxShadow = '0 0 20px #0FFCBE, 0 0 30px #106EBE';
            navbar.style.transition = 'box-shadow 0.3s ease';
        });
        navbar.addEventListener('mouseleave', () => {
            navbar.style.boxShadow = 'none';
        });
    }

    // Highlight Active Nav Link
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
            link.style.backgroundColor = '#0FFCBE';
            link.style.color = '#106EBE';
            link.style.boxShadow = 'inset 0 0 10px #106EBE';
        }
    });
});