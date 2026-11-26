document.addEventListener('DOMContentLoaded', () => {
    const themeToggleBtn = document.getElementById('theme-toggle');
    const htmlElement = document.documentElement;

    const savedTheme = localStorage.getItem('site-theme');
    if (savedTheme === 'dark') {
        htmlElement.setAttribute('data-theme', 'dark');
        if (themeToggleBtn) themeToggleBtn.textContent = '☀️ Светлая';
    }

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const isDark = htmlElement.getAttribute('data-theme') === 'dark';

            if (isDark) {
                htmlElement.removeAttribute('data-theme');
                localStorage.setItem('site-theme', 'light');
                themeToggleBtn.textContent = '🌙 Тёмная';
            } else {
                htmlElement.setAttribute('data-theme', 'dark');
                localStorage.setItem('site-theme', 'dark');
                themeToggleBtn.textContent = '☀️ Светлая';
            }
        });
    }
});