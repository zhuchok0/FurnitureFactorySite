(function () {
    'use strict';

    const norm = (s) => String(s === undefined || s === null ? '' : s).trim().toLowerCase();
    const fullName = (d) => [d.lastName, d.firstName, d.patronymic].filter(Boolean).join(' ');
    const CLASS_LABELS = { economy: 'Эконом', business: 'Бизнес' };

    function val(form, name) {
        const f = form.elements[name];
        return f ? String(f.value).trim() : '';
    }

    function findNamesakes(list, flight) {
        const groups = new Map();
        list.forEach((p) => {
            const d = p.getData();
            if (norm(d.flight) !== norm(flight)) return;
            const key = norm(d.lastName);
            if (!groups.has(key)) groups.set(key, []);
            groups.get(key).push(d);
        });
        return Array.from(groups.values()).filter((g) => g.length > 1);
    }

    function renderTable(container, headers, rows) {
        container.textContent = '';
        if (!rows.length) {
            const p = document.createElement('p');
            p.textContent = 'Список пассажиров пуст.';
            container.appendChild(p);
            return;
        }
        const table = document.createElement('table');
        table.className = 'pax-table';
        const thead = table.createTHead().insertRow();
        headers.forEach((h) => {
            const th = document.createElement('th');
            th.textContent = h;
            thead.appendChild(th);
        });
        const tbody = table.createTBody();
        rows.forEach((row) => {
            const tr = tbody.insertRow();
            row.forEach((cell) => { tr.insertCell().textContent = cell; });
        });
        container.appendChild(table);
    }

    function renderResult(container, flight, groups, describe) {
        container.textContent = '';
        const title = document.createElement('p');
        title.textContent = 'Рейс «' + flight + '»:';
        container.appendChild(title);

        if (!groups.length) {
            const p = document.createElement('p');
            p.textContent = 'Однофамильцев на этом рейсе нет.';
            container.appendChild(p);
            return;
        }
        const ul = document.createElement('ul');
        groups.forEach((g) => {
            const li = document.createElement('li');
            const strong = document.createElement('strong');
            strong.textContent = g[0].lastName + ' (' + g.length + '): ';
            li.appendChild(strong);
            li.appendChild(document.createTextNode(g.map(describe).join('; ')));
            ul.appendChild(li);
        });
        container.appendChild(ul);
    }

    // ???
    window.PaxUtil = {
        val, fullName, findNamesakes, renderTable, renderResult,
        classLabel: (c) => CLASS_LABELS[c] || '—'
    };
})();