(function () {
    'use strict';

    const variants = { proto: window.PaxProto, class: window.PaxClass };

    const SAMPLE = [
        ['Иванов', 'Иван', 'Иванович', 'SU101', '12A', 'business'],
        ['Иванов', 'Пётр', 'Сергеевич', 'SU101', '12B', 'economy'],
        ['Петрова', 'Мария', 'Олеговна', 'SU101', '14C', 'economy'],
        ['Иванов', 'Сергей', 'Петрович', 'SU101', '20D', 'economy'],
        ['Сидоров', 'Алексей', 'Петрович', 'SU101', '3A', 'business'],
        ['Смирнов', 'Андрей', 'Игоревич', 'SU202', '8F', 'economy'],
        ['Смирнов', 'Павел', 'Андреевич', 'SU303', '9A', 'economy']
    ];

    document.querySelectorAll('.pax').forEach((section) => {
        const V = variants[section.dataset.variant];
        if (!V) return;

        const list = [];
        const form = section.querySelector('.pax-form');
        const searchForm = section.querySelector('.pax-search');
        const listBox = section.querySelector('.pax-list');
        const resultBox = section.querySelector('.pax-result');
        const msg = section.querySelector('.pax-msg');
        const kind = form.elements.kind;

        const make = () => (kind.value === 'ext' ? new V.TicketedPassenger() : new V.Passenger());

        function toggleExt() {
            section.querySelectorAll('.pax-ext').forEach((el) => { el.hidden = kind.value !== 'ext'; });
        }
        const refresh = () => make().renderAll(list, listBox);

        kind.addEventListener('change', () => { toggleExt(); refresh(); });

        form.addEventListener('submit', (e) => {
            e.preventDefault();
            msg.textContent = '';
            if (!make().addFromForm(form, list)) {
                msg.textContent = 'Заполните фамилию, имя и рейс.';
                return;
            }
            ['lastName', 'firstName', 'patronymic', 'seat'].forEach((n) => { form.elements[n].value = ''; });
            refresh();
            form.elements.lastName.focus();
        });

        searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const flight = searchForm.elements.searchFlight.value.trim();
            if (!flight) return;
            make().renderResult(list, flight, resultBox);
        });

        section.querySelector('.pax-sample').addEventListener('click', () => {
            SAMPLE.forEach((s) => {
                const p = (s[4] ? new V.TicketedPassenger() : new V.Passenger());
                p.setData({ lastName: s[0], firstName: s[1], patronymic: s[2], flight: s[3],
                            seat: s[4], ticketClass: s[5] });
                list.push(p);
            });
            searchForm.elements.searchFlight.value = 'SU101';
            refresh();
        });

        toggleExt();
        refresh();
    });
})();