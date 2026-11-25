(function () {
    'use strict';
    const U = window.PaxUtil;

    // ----- Базовый конструктор -----
    function Passenger(lastName, firstName, patronymic, flight) {
        this.lastName = lastName || '';
        this.firstName = firstName || '';
        this.patronymic = patronymic || '';
        this.flight = flight || '';
    }

    // 1) геттер
    Passenger.prototype.getData = function () {
        return {
            lastName: this.lastName,
            firstName: this.firstName,
            patronymic: this.patronymic,
            flight: this.flight
        };
    };

    // 2) сеттер
    Passenger.prototype.setData = function (d) {
        const self = this;
        ['lastName', 'firstName', 'patronymic', 'flight'].forEach(function (k) {
            if (d[k] !== undefined) self[k] = String(d[k]).trim();
        });
    };

    // 3) добавление объекта из компонентов формы
    Passenger.prototype.addFromForm = function (form, list) {
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
    };

    // 4) вывод всех объектов массива
    Passenger.prototype.renderAll = function (list, container) {
        U.renderTable(container, ['№', 'Фамилия', 'Имя', 'Отчество', 'Рейс'],
            list.map(function (p, i) {
                const d = p.getData();
                return [i + 1, d.lastName, d.firstName, d.patronymic || '—', d.flight];
            }));
    };

    // 5) вывод результата (однофамильцы на рейсе)
    Passenger.prototype.renderResult = function (list, flight, container) {
        U.renderResult(container, flight, U.findNamesakes(list, flight), U.fullName);
    };

    // ----- Наследник -----
    function TicketedPassenger(lastName, firstName, patronymic, flight, seat, ticketClass) {
        Passenger.call(this, lastName, firstName, patronymic, flight);
        this.seat = seat || '';
        this.ticketClass = ticketClass || 'economy';
    }
    TicketedPassenger.prototype = Object.create(Passenger.prototype);
    TicketedPassenger.prototype.constructor = TicketedPassenger;

    TicketedPassenger.prototype.getData = function () {
        const d = Passenger.prototype.getData.call(this);
        d.seat = this.seat;
        d.ticketClass = this.ticketClass;
        return d;
    };

    TicketedPassenger.prototype.setData = function (d) {
        Passenger.prototype.setData.call(this, d);
        if (d.seat !== undefined) this.seat = String(d.seat).trim();
        if (d.ticketClass !== undefined) this.ticketClass = d.ticketClass;
    };

    TicketedPassenger.prototype.addFromForm = function (form, list) {
        const ok = Passenger.prototype.addFromForm.call(this, form, list);
        if (ok) {
            this.setData({ seat: U.val(form, 'seat'), ticketClass: U.val(form, 'ticketClass') || 'economy' });
        }
        return ok;
    };

    TicketedPassenger.prototype.renderAll = function (list, container) {
        U.renderTable(container, ['№', 'Фамилия', 'Имя', 'Отчество', 'Рейс', 'Место', 'Класс'],
            list.map(function (p, i) {
                const d = p.getData();
                return [i + 1, d.lastName, d.firstName, d.patronymic || '—', d.flight,
                        d.seat || '—', U.classLabel(d.ticketClass)];
            }));
    };

    TicketedPassenger.prototype.renderResult = function (list, flight, container) {
        U.renderResult(container, flight, U.findNamesakes(list, flight), function (d) {
            return U.fullName(d) + ' (место ' + (d.seat || '—') + ', ' + U.classLabel(d.ticketClass) + ')';
        });
    };

    window.PaxProto = { Passenger: Passenger, TicketedPassenger: TicketedPassenger };
})();