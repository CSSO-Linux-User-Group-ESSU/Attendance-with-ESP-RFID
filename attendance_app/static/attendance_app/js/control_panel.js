const currentUrl = window.location.pathname;
const navLinks = document.querySelectorAll('.nav-buttons');
const toggleButton = document.getElementById('toggle-btn')
const sidebar = document.querySelector('nav')


navLinks.forEach(link => {
    if (link.href.includes(currentUrl)) {
        link.classList.add('nav-active');
    }
});


/* Open side bar */
function showSidebar() {
    const sidebar = document.querySelector('.sidebar');
    sidebar.style.display = 'flex';
}

/* Close side bar */
function hideSidebar() {
    sidebar.style.display = "none";
}

/* Show active link on laptop devices sidebar list */
document.addEventListener("DOMContentLoaded", function () {
    const links = document.querySelectorAll(".nav-link");

    function setActiveLink(event) {
        const clickedLink = event.target;
        const allMenus = document.querySelectorAll("nav, .nav-link");

        // Remove "active" class from all links in both sidebar and navbar
        allMenus.forEach(menu => {
            menu.querySelectorAll(".nav-link").forEach(link => link.classList.remove("active"));
        });

        // Add "active" class to the clicked link
        clickedLink.classList.add("active");

        // Save active link in localStorage to persist after refresh
        localStorage.setItem("activeNavLink", clickedLink.getAttribute("href"));
    }

    // Attach event listener to all links
    links.forEach(link => link.addEventListener("click", setActiveLink));

    // Restore active link from localStorage after page reload
    const savedActiveLink = localStorage.getItem("activeNavLink");
    if (savedActiveLink) {
        document.querySelectorAll(`.nav-link[href="${savedActiveLink}"]`).forEach(link => link.classList.add("active"));
    }
});

// Toggle sidebar button

function toggleSidebar(){
    sidebar.classList.toggle('close-sidebar')
    toggleButton.classList.toggle('rotate')
}