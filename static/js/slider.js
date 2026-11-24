class ImageSlider {
    constructor(containerSelector, options = {}) {
        this.container = document.querySelector(containerSelector);
        if (!this.container) return;

        this.options = Object.assign({
            loop: true,
            navs: true,
            pags: true,
            auto: true,
            stopMouseHover: true,
            delay: 5,
            visibleItems: 1
        }, options);

        this.slides = Array.from(this.container.querySelectorAll('.slider-slide'));
        this.currentIndex = 0;
        this.timer = null;

        if (this.slides.length === 0) return;

        this.initDOM();
        this.initEvents();
        this.updateSlider();

        if (this.options.auto) {
            this.startAutoplay();
        }
    }

    initDOM() {
        // Создаем обертку-трек для картинок
        this.track = document.createElement('div');
        this.track.className = 'slider-track';

        this.slides.forEach(slide => {
            this.track.appendChild(slide);
            slide.classList.add('slider-slide-item');
        });
        this.container.appendChild(this.track);

        // Индикатор номера (например, 1/3)
        this.counter = document.createElement('div');
        this.counter.className = 'slider-counter';
        this.container.appendChild(this.counter);

        // Навигация (стрелочки)
        if (this.options.navs) {
            this.prevBtn = document.createElement('button');
            this.prevBtn.className = 'slider-btn slider-btn-prev';
            this.prevBtn.innerHTML = '&#10094;';

            this.nextBtn = document.createElement('button');
            this.nextBtn.className = 'slider-btn slider-btn-next';
            this.nextBtn.innerHTML = '&#10095;';

            this.container.appendChild(this.prevBtn);
            this.container.appendChild(this.nextBtn);
        }

        // Пагинация (точки по количеству возможных страниц сдвига)
        if (this.options.pags) {
            this.pagsContainer = document.createElement('div');
            this.pagsContainer.className = 'slider-pagination';

            const totalPages = this.getTotalPages();
            for (let i = 0; i < totalPages; i++) {
                const dot = document.createElement('button');
                dot.className = 'slider-dot';
                dot.dataset.index = i;
                this.pagsContainer.appendChild(dot);
            }
            this.container.appendChild(this.pagsContainer);
        }
    }

    getTotalPages() {
        // Максимальное количество страниц для сдвига
        return Math.max(1, this.slides.length);
    }

    initEvents() {
        if (this.options.navs) {
            this.prevBtn.addEventListener('click', () => this.prev());
            this.nextBtn.addEventListener('click', () => this.next());
        }

        if (this.options.pags) {
            this.pagsContainer.addEventListener('click', (e) => {
                if (e.target.classList.contains('slider-dot')) {
                    const index = parseInt(e.target.dataset.index, 10);
                    this.goTo(index);
                }
            });
        }

        if (this.options.auto && this.options.stopMouseHover) {
            this.container.addEventListener('mouseenter', () => this.stopAutoplay());
            this.container.addEventListener('mouseleave', () => this.startAutoplay());
        }
    }

    updateSlider() {
        const totalPages = this.getTotalPages();

        // Смещение трека в процентах для показа нужной группы картинок
        const offset = -(this.currentIndex * 100);
        this.track.style.transform = `translateX(${offset}%)`;

        // Обновление счетчика (например, текущая группа / всего групп)
        if (this.counter) {
            this.counter.textContent = `${this.currentIndex + 1} / ${totalPages}`;
        }

        // Обновление пагинации
        if (this.options.pags) {
            const dots = this.pagsContainer.querySelectorAll('.slider-dot');
            dots.forEach((dot, index) => {
                if (index === this.currentIndex) {
                    dot.classList.add('active');
                } else {
                    dot.classList.remove('active');
                }
            });
        }
    }

    next() {
        const totalPages = this.getTotalPages();
        if (this.currentIndex < totalPages - 1) {
            this.currentIndex++;
        } else if (this.options.loop) {
            this.currentIndex = 0;
        }
        this.updateSlider();
    }

    prev() {
        const totalPages = this.getTotalPages();
        if (this.currentIndex > 0) {
            this.currentIndex--;
        } else if (this.options.loop) {
            this.currentIndex = totalPages - 1;
        }
        this.updateSlider();
    }

    goTo(index) {
        const totalPages = this.getTotalPages();
        if (index >= 0 && index < totalPages) {
            this.currentIndex = index;
            this.updateSlider();
        }
    }

    startAutoplay() {
        if (this.timer) clearInterval(this.timer);
        const intervalTime = (this.options.delay || 5) * 1000;
        this.timer = setInterval(() => {
            this.next();
        }, intervalTime);
    }

    stopAutoplay() {
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }
    }

    setDelay(newDelay) {
        this.options.delay = parseFloat(newDelay) || 5;
        if (this.options.auto) {
            this.startAutoplay();
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const sliderEl = document.getElementById('my-image-slider');
    if (!sliderEl) return;

    const mySlider = new ImageSlider('#my-image-slider', {
        loop: true,
        navs: true,
        pags: true,
        auto: true,
        stopMouseHover: true,
        delay: 5,
        visibleItems: 1
    });

    const applyBtn = document.getElementById('apply-delay-btn');
    const delayInput = document.getElementById('slider-delay-input');

    if (applyBtn && delayInput) {
        applyBtn.addEventListener('click', () => {
            mySlider.setDelay(delayInput.value);
            alert(`Время показа слайда изменено на ${delayInput.value} сек.`);
        });
    }
});