const currentUrl = window.location.pathname;

const navLinks = document.querySelectorAll('.nav-buttons');

navLinks.forEach(link => {
    if (link.href.includes(currentUrl)) {
        link.classList.add('nav-active');
    }
});