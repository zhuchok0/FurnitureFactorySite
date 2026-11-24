document.addEventListener('DOMContentLoaded', () => {
    const SESSION_KEY = 'birthCheckCompleted_v1';

    // Не повторяем запрос на каждой странице в рамках одной вкладки/сессии
    if (sessionStorage.getItem(SESSION_KEY) === 'true') {
        return;
    }

    function parseBirthDate(raw) {
        if (!raw) return null;
        const value = raw.trim();

        // Поддержка форматов ГГГГ-ММ-ДД и ДД.ММ.ГГГГ
        let year, month, day;
        if (/^\d{4}-\d{2}-\d{2}$/.test(value)) {
            [year, month, day] = value.split('-').map(Number);
        } else if (/^\d{2}\.\d{2}\.\d{4}$/.test(value)) {
            [day, month, year] = value.split('.').map(Number);
        } else {
            return null;
        }

        const date = new Date(year, month - 1, day);
        if (
            date.getFullYear() !== year ||
            date.getMonth() !== month - 1 ||
            date.getDate() !== day
        ) {
            return null;
        }

        return date;
    }

    function calculateAge(birthDate, today = new Date()) {
        let age = today.getFullYear() - birthDate.getFullYear();
        const monthDiff = today.getMonth() - birthDate.getMonth();

        if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
            age--;
        }
        return age;
    }

    const input = prompt('Введите вашу дату рождения (в формате ДД.ММ.ГГГГ или ГГГГ-ММ-ДД):');
    if (input === null) {
        return;
    }

    const birthDate = parseBirthDate(input);
    const today = new Date();

    if (!birthDate || birthDate > today) {
        alert('Введена некорректная дата рождения.');
        return;
    }

    const age = calculateAge(birthDate, today);
    sessionStorage.setItem(SESSION_KEY, 'true');

    if (age >= 18) {
        const daysOfWeek = [
            'воскресенье',
            'понедельник',
            'вторник',
            'среда',
            'четверг',
            'пятница',
            'суббота'
        ];
        const dayName = daysOfWeek[birthDate.getDay()];
        alert(`Вам ${age} лет. День недели вашей даты рождения: ${dayName}.`);
    } else {
        alert(`Вам ${age} лет. Для использования сайта необходимо разрешение родителей.`);
    }
});