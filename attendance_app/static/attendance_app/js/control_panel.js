const currentUrl = window.location.pathname;

const navLinks = document.querySelectorAll('.nav-buttons');

navLinks.forEach(link => {
    if (link.href.includes(currentUrl)) {
        link.classList.add('nav-active');
    }
});

/* Open side bar */
const sidebar = document.querySelector(".sidebar");

function showSidebar() {
    sidebar.style.display = "flex";
}

/* Close side bar */
function hideSidebar() {
    sidebar.style.display = "none";
}
