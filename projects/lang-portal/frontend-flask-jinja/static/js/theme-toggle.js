
console.log('Theme toggle script loaded');

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded and parsed');
    const themeToggle = document.getElementById('theme-toggle');
    if (!themeToggle) {
        console.error('Theme toggle button not found!');
        return;
    }
    
    console.log('Checking local storage for theme:', localStorage.getItem('theme'));
    
    if (localStorage.getItem('theme') === 'dark') {
        document.body.classList.add('dark-mode');
        console.log('Dark mode activated from storage');
    }
    
    themeToggle.addEventListener('click', function() {
        document.body.classList.toggle('dark-mode');
        localStorage.setItem('theme', document.body.classList.contains('dark-mode') ? 'dark' : 'light');
        console.log('Toggled theme, new mode:', localStorage.getItem('theme'));
    });
});
