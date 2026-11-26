(function () {
    'use strict';

    const items = document.querySelectorAll('[data-reveal]');
    if (!items.length || !('IntersectionObserver' in window) || !items[0].animate) return;

    const variants = {
        up:    { from: 'translateY(90px) rotate(-3deg) scale(0.9)' },
        left:  { from: 'translateX(-120px) rotate(-6deg) scale(0.9)' },
        right: { from: 'translateX(120px) rotate(6deg) scale(0.9)' },
        zoom:  { from: 'scale(0.5) rotate(-8deg)' }
    };

    function buildFrames(kind) {
        const v = variants[kind] || variants.up;
        return [
            { opacity: 0,   transform: v.from,                          filter: 'blur(10px)', offset: 0 },
            { opacity: 1,   transform: 'translate(0,-12px) scale(1.04)', filter: 'blur(0)',    offset: 0.7 },
            { opacity: 1,   transform: 'translate(0,0) scale(1)',        filter: 'blur(0)',    offset: 1 }
        ];
    }

    function play(el, delay) {
        const animation = el.animate(buildFrames(el.dataset.reveal), {
            duration: 1000,
            delay: delay,
            easing: 'cubic-bezier(0.22, 1.2, 0.36, 1)', // небольшой «отскок»
            fill: 'both'
        });
        animation.finished.then(() => {
            el.style.opacity = '';
            animation.cancel();
        }).catch(() => {});
    }

    items.forEach((el) => { el.style.opacity = '0'; });

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (!entry.isIntersecting) return;
            const el = entry.target;
            const base = parseInt(el.dataset.revealDelay || '0', 10);
            play(el, base);

            if (el.hasAttribute('data-reveal-stagger')) {
                Array.from(el.children).forEach((child, i) => {
                    child.style.opacity = '0';
                    const a = child.animate(buildFrames('up'), {
                        duration: 800,
                        delay: base + 250 + i * 150,
                        easing: 'ease-out',
                        fill: 'both'
                    });
                    a.finished.then(() => { child.style.opacity = ''; a.cancel(); }).catch(() => {});
                });
            }
            observer.unobserve(el);
        });
    }, { threshold: 0.1 });

    items.forEach((el) => observer.observe(el));
})();