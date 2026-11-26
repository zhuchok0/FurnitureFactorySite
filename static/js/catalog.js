document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.catalog-card').forEach((card) => {
        card.addEventListener('mousemove', (e) => {
            const r = card.getBoundingClientRect();
            const x = (e.clientX - r.left) / r.width - 0.5;
            const y = (e.clientY - r.top) / r.height - 0.5;
            card.style.setProperty('--rotateX', `${(-y * 28).toFixed(1)}deg`);
            card.style.setProperty('--rotateY', `${(x * 28).toFixed(1)}deg`);
            card.style.setProperty('--posx', `${((x + 0.5) * 100).toFixed(0)}%`);
            card.style.setProperty('--posy', `${((y + 0.5) * 100).toFixed(0)}%`);
        });

        card.addEventListener('mouseleave', () => {
            ['--rotateX', '--rotateY', '--posx', '--posy'].forEach((p) => card.style.removeProperty(p));
        });
    });

    const perPage = document.getElementById('per-page-select');
    if (perPage) perPage.addEventListener('change', () => perPage.form.submit());
});