document.addEventListener('DOMContentLoaded', () => {
    const themeCheckbox = document.getElementById('theme-checkbox');
    const body = document.body;

    // Function to apply the theme
    const applyTheme = (theme) => {
        if (theme === 'dark-theme') {
            body.classList.add('dark-theme');
            themeCheckbox.checked = true;
        } else {
            body.classList.remove('dark-theme');
            themeCheckbox.checked = false;
        }
    };

    // Check for saved theme in localStorage and apply it
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        applyTheme(savedTheme);
    }

    // Listen for toggle switch change
    themeCheckbox.addEventListener('change', () => {
        if (themeCheckbox.checked) {
            localStorage.setItem('theme', 'dark-theme');
            applyTheme('dark-theme');
        } else {
            localStorage.setItem('theme', 'light-theme');
            applyTheme('light-theme');
        }
    });
});