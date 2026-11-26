(function () {
    'use strict';
    const U = window.PaxUtil;

    class Passenger {
        constructor(lastName = '', firstName = '', patronymic = '', flight = '') {
            this.lastName = lastName;
            this.firstName = firstName;
            this.patronymic = patronymic;
            this.flight = flight;
        }

        getData() {
            return {
                lastName: this.lastName,
                firstName: this.firstName,
                patronymic: this.patronymic,
                flight: this.flight
            };
        }

        setData(d) {
            ['lastName', 'firstName', 'patronymic', 'flight'].forEach((k) => {
                if (d[k] !== undefined) this[k] = String(d[k]).trim();
            });
        }

        addFromForm(form, list) {
            const d = {
                lastName: U.val(form, 'lastName'),
                firstName: U.val(form, 'firstName'),
                patronymic: U.val(form, 'patronymic'),
                flight: U.val(form, 'flight')
            };
            if (!d.lastName || !d.firstName || !d.flight) return false;
            this.setData(d);
            list.push(this);
            return true;
        }

        renderAll(list, container) {
            U.renderTable(container, ['№', 'Фамилия', 'Имя', 'Отчество', 'Рейс'],
                list.map((p, i) => {
                    const d = p.getData();
                    return [i + 1, d.lastName, d.firstName, d.patronymic || '—', d.flight];
                }));
        }

        renderResult(list, flight, container) {
            U.renderResult(container, flight, U.findNamesakes(list, flight), U.fullName);
        }
    }

    class TicketedPassenger extends Passenger {
        constructor(lastName, firstName, patronymic, flight, seat = '', ticketClass = 'economy') {
            super(lastName, firstName, patronymic, flight);
            this.seat = seat;
            this.ticketClass = ticketClass;
        }

        getData() {
            return { ...super.getData(), seat: this.seat, ticketClass: this.ticketClass };
        }

        setData(d) {
            super.setData(d);
            if (d.seat !== undefined) this.seat = String(d.seat).trim();
            if (d.ticketClass !== undefined) this.ticketClass = d.ticketClass;
        }

        addFromForm(form, list) {
            const ok = super.addFromForm(form, list);
            if (ok) {
                this.setData({ seat: U.val(form, 'seat'), ticketClass: U.val(form, 'ticketClass') || 'economy' });
            }
            return ok;
        }

        renderAll(list, container) {
            U.renderTable(container, ['№', 'Фамилия', 'Имя', 'Отчество', 'Рейс', 'Место', 'Класс'],
                list.map((p, i) => {
                    const d = p.getData();
                    return [i + 1, d.lastName, d.firstName, d.patronymic || '—', d.flight,
                            d.seat || '—', U.classLabel(d.ticketClass)];
                }));
        }

        renderResult(list, flight, container) {
            U.renderResult(container, flight, U.findNamesakes(list, flight),
                (d) => U.fullName(d) + ' (место ' + (d.seat || '—') + ', ' + U.classLabel(d.ticketClass) + ')');
        }
    }

    window.PaxClass = { Passenger, TicketedPassenger };
})();