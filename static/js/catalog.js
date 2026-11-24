document.addEventListener('DOMContentLoaded', () => {
    const sectionEl = document.getElementById('furniture-items-section');
    const dynamicEl = document.getElementById('catalog-items-dynamic');
    if (!sectionEl || !dynamicEl) return;

    function initCardTilt(root = document) {
        const cards = root.querySelectorAll('.catalog-card');

        cards.forEach((card) => {
            if (card.dataset.tiltInitialized === 'true') return;
            card.dataset.tiltInitialized = 'true';

            let resetTimer = null;

            card.addEventListener('mouseenter', () => {
                if (resetTimer) {
                    clearTimeout(resetTimer);
                    resetTimer = null;
                }
                card.style.animation = 'none';
            });

            card.addEventListener('mousemove', (event) => {
                const rect = card.getBoundingClientRect();
                const width = rect.width || 1;
                const height = rect.height || 1;

                const x = event.clientX - rect.left;
                const y = event.clientY - rect.top;

                const middleX = width / 2;
                const middleY = height / 2;

                const normX = (x - middleX) / middleX;
                const normY = (y - middleY) / middleY;

                const tiltX = (normX * 14).toFixed(2);
                const tiltY = (-normY * 14).toFixed(2);

                const posX = (50 + normX * 25).toFixed(1);
                const posY = (50 - normY * 20).toFixed(1);

                card.style.setProperty('--rotateX', `${tiltX}deg`);
                card.style.setProperty('--rotateY', `${tiltY}deg`);
                card.style.setProperty('--posx', `${posX}%`);
                card.style.setProperty('--posy', `${posY}%`);
            });

            card.addEventListener('mouseleave', () => {
                card.style.animation = 'reset-card 0.6s ease forwards';

                resetTimer = setTimeout(() => {
                    card.style.animation = 'none';
                    card.style.setProperty('--rotateX', '0deg');
                    card.style.setProperty('--rotateY', '0deg');
                    card.style.setProperty('--posx', '50%');
                    card.style.setProperty('--posy', '50%');
                    resetTimer = null;
                }, 600);
            });
        });
    }

    function scrollToCatalogSection() {
        const top = sectionEl.getBoundingClientRect().top + window.scrollY - 16;
        window.scrollTo({
            top: Math.max(0, top),
            behavior: 'smooth'
        });
    }

    async function loadCatalogFragment(url, pushHistory = true) {
        dynamicEl.style.opacity = '0.5';
        try {
            const response = await fetch(url, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const html = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const nextDynamic = doc.getElementById('catalog-items-dynamic');

            if (nextDynamic) {
                dynamicEl.innerHTML = nextDynamic.innerHTML;
                initCardTilt(dynamicEl);
                if (pushHistory) {
                    window.history.pushState({}, '', url);
                }
                scrollToCatalogSection();
            } else {
                window.location.href = url;
            }
        } catch (err) {
            console.error('Ошибка обновления списка мебели:', err);
            window.location.href = url;
        } finally {
            dynamicEl.style.opacity = '1';
        }
    }

    // Перехватываем клики по ссылкам пагинации и сортировки внутри секции мебели
    sectionEl.addEventListener('click', (e) => {
        const link = e.target.closest('a');
        if (!link) return;
        const href = link.getAttribute('href');
        if (!href || !href.startsWith('?')) return;

        e.preventDefault();
        loadCatalogFragment(href, true);
    });

    // Перехватываем смену количества элементов на странице
    sectionEl.addEventListener('change', (e) => {
        if (e.target && e.target.id === 'per-page-select') {
            const form = e.target.closest('form');
            if (!form) return;
            const params = new URLSearchParams(new FormData(form));
            params.delete('page'); // при смене per_page возвращаемся на 1-ю страницу
            loadCatalogFragment('?' + params.toString(), true);
        }
    });

    // Поддержка кнопок «Назад / Вперёд» в браузере
    // Поддержка кнопок «Назад / Вперёд» в браузере
    window.addEventListener('popstate', () => {
        loadCatalogFragment(window.location.search || '?', false);
    });

    initCardTilt(document);
});