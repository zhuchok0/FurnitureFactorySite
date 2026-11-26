(function () {
    'use strict';

    const scene = document.querySelector('[data-chairs-scene]');
    if (!scene) return;

    const chairs = Array.from(scene.querySelectorAll('[data-chair]')).map((el) => ({
        el,
        x: parseFloat(el.dataset.x),
        y: parseFloat(el.dataset.y),
        spin: parseFloat(el.dataset.spin),
        start: parseFloat(el.dataset.start) || 0,
        speed: parseFloat(el.dataset.speed),
        sway: parseFloat(el.dataset.sway) || 0,
        phase: parseFloat(el.dataset.phase) || 0
    }));

    chairs.forEach((c) => {
        c.el.style.left = c.x + '%';
        c.el.style.top = c.y + '%';
    });

    const clamp = (v, min, max) => Math.min(max, Math.max(min, v));
    let target = 0, current = 0, running = false;

    function readProgress() {
        const rect = scene.getBoundingClientRect();
        const vh = window.innerHeight;
        return clamp((vh - rect.top) / (vh + rect.height), 0, 1);
    }

    function render(p) {
        const h = scene.offsetHeight;
        chairs.forEach((c) => {
            const angle = c.start + p * c.spin * 360;
            const dy = (p - 0.5) * c.speed * h;
            const dx = Math.sin(p * Math.PI * 2 + c.phase) * c.sway;
            const scale = 0.85 + 0.3 * Math.sin(p * Math.PI);
            c.el.style.transform =
                `translate3d(${dx}px,${dy}px,0) rotate(${angle}deg) scale(${scale})`;
        });
    }

    function tick() {
        current += (target - current) * 0.12;
        if (Math.abs(target - current) < 0.0005) {
            current = target;
            running = false;
        }
        render(current);
        if (running) requestAnimationFrame(tick);
    }

    function onScroll() {
        target = readProgress();
        if (!running) {
            running = true;
            requestAnimationFrame(tick);
        }
    }

    window.addEventListener('scroll', onScroll, { passive: true });
    current = target = readProgress();
    render(current);
})();