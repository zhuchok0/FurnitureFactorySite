(function () {
    'use strict';

    const $ = (id) => document.getElementById(id);
    const setBadge = (el, ok) => {
        el.textContent = ok ? 'поддерживается' : 'не поддерживается';
        el.className = 'api-badge ' + (ok ? 'api-badge--ok' : 'api-badge--no');
    };

    // =====================================================
    // 2) Синтез речи (объявлен первым: им пользуются остальные блоки)
    // =====================================================
    const synth = 'speechSynthesis' in window ? window.speechSynthesis : null;
    const ttsVoice = $('ttsVoice');
    const ttsStatus = $('ttsStatus');
    let voices = [];

    setBadge($('ttsSupport'), !!synth);

    function loadVoices() {
        const all = synth.getVoices();
        // русские голоса — первыми
        voices = all.slice().sort((a, b) =>
            (b.lang.toLowerCase().startsWith('ru') ? 1 : 0) - (a.lang.toLowerCase().startsWith('ru') ? 1 : 0));
        const prev = ttsVoice.value;
        ttsVoice.textContent = '';
        voices.forEach((v, i) => {
            const opt = document.createElement('option');
            opt.value = i;
            opt.textContent = v.name + ' (' + v.lang + ')';
            ttsVoice.appendChild(opt);
        });
        if (prev) ttsVoice.value = prev;
    }

    function speak(text) {
        if (!synth) {
            alert('Ваш браузер не поддерживает синтез речи.');
            return;
        }
        synth.cancel();
        const u = new SpeechSynthesisUtterance(text);
        const voice = voices[ttsVoice.value];
        if (voice) {
            u.voice = voice;
            u.lang = voice.lang;
        } else {
            u.lang = 'ru-RU';
        }
        u.rate = Number($('ttsRate').value);
        u.pitch = Number($('ttsPitch').value);
        u.onstart = () => { ttsStatus.textContent = 'Говорит…'; };
        u.onend = () => { ttsStatus.textContent = 'Готово.'; };
        u.onerror = (e) => { ttsStatus.textContent = 'Ошибка синтеза: ' + e.error; };
        synth.speak(u);
    }

    if (synth) {
        loadVoices();
        synth.addEventListener('voiceschanged', loadVoices); // голоса загружаются асинхронно

        $('ttsRate').addEventListener('input', (e) => { $('ttsRateVal').textContent = e.target.value; });
        $('ttsPitch').addEventListener('input', (e) => { $('ttsPitchVal').textContent = e.target.value; });
        $('ttsSpeak').addEventListener('click', () => {
            const text = $('ttsText').value.trim();
            if (text) speak(text);
        });
        $('ttsPause').addEventListener('click', () => { synth.pause(); ttsStatus.textContent = 'Пауза.'; });
        $('ttsResume').addEventListener('click', () => { synth.resume(); ttsStatus.textContent = 'Говорит…'; });
        $('ttsStop').addEventListener('click', () => { synth.cancel(); ttsStatus.textContent = 'Остановлено.'; });
    } else {
        ['ttsSpeak', 'ttsPause', 'ttsResume', 'ttsStop'].forEach((id) => { $(id).disabled = true; });
    }

    // =====================================================
    // 1) Геолокация
    // =====================================================
    const geoSupported = 'geolocation' in navigator;
    const geoMsg = $('geoMsg');
    const geoSpeakBtn = $('geoSpeak');
    let geoText = '';
    let watchId = null;

    setBadge($('geoSupport'), geoSupported);

    const GEO_ERRORS = {
        1: 'Доступ к геолокации запрещён. Разрешите его в настройках браузера или системы.',
        2: 'Не удалось определить положение (сигнал недоступен).',
        3: 'Превышено время ожидания ответа.'
    };

    function showPosition(pos) {
        const c = pos.coords;
        const lat = c.latitude.toFixed(5);
        const lon = c.longitude.toFixed(5);
        $('geoLat').textContent = lat + '°';
        $('geoLon').textContent = lon + '°';
        $('geoAcc').textContent = '±' + Math.round(c.accuracy) + ' м';
        $('geoAlt').textContent = c.altitude === null ? 'нет данных' : Math.round(c.altitude) + ' м';
        $('geoSpeed').textContent = c.speed === null ? 'нет данных' : (c.speed * 3.6).toFixed(1) + ' км/ч';
        $('geoTime').textContent = new Date(pos.timestamp).toLocaleTimeString('ru-RU');

        const map = $('geoMap');
        map.href = 'https://www.openstreetmap.org/?mlat=' + lat + '&mlon=' + lon +
                   '#map=15/' + lat + '/' + lon;
        map.hidden = false;

        geoMsg.textContent = '';
        geoText = 'Ваши координаты: широта ' + c.latitude.toFixed(3) + ', долгота ' +
                  c.longitude.toFixed(3) + '. Точность около ' + Math.round(c.accuracy) + ' метров.';
        geoSpeakBtn.disabled = false;
    }

    function geoError(err) {
        geoMsg.textContent = GEO_ERRORS[err.code] || ('Ошибка геолокации: ' + err.message);
    }

    const GEO_OPTIONS = { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 };

    if (geoSupported) {
        $('geoOnce').addEventListener('click', () => {
            geoMsg.textContent = 'Определяю местоположение…';
            navigator.geolocation.getCurrentPosition(showPosition, geoError, GEO_OPTIONS);
        });

        $('geoWatch').addEventListener('click', (e) => {
            if (watchId === null) {
                geoMsg.textContent = 'Слежение включено…';
                watchId = navigator.geolocation.watchPosition(showPosition, geoError, GEO_OPTIONS);
                e.target.textContent = 'Остановить слежение';
            } else {
                navigator.geolocation.clearWatch(watchId);
                watchId = null;
                geoMsg.textContent = 'Слежение остановлено.';
                e.target.textContent = 'Следить за перемещением';
            }
        });

        geoSpeakBtn.addEventListener('click', () => speak(geoText));
    } else {
        ['geoOnce', 'geoWatch'].forEach((id) => { $(id).disabled = true; });
        geoMsg.textContent = 'Geolocation API не поддерживается этим браузером.';
    }

    // =====================================================
    // 3) Состояние батареи
    // =====================================================
    const batMsg = $('batMsg');
    const batSupported = typeof navigator.getBattery === 'function';
    let batText = '';

    setBadge($('batSupport'), batSupported);

    function formatTime(sec) {
        if (!isFinite(sec)) return '—';
        const h = Math.floor(sec / 3600);
        const m = Math.round((sec % 3600) / 60);
        return (h ? h + ' ч ' : '') + m + ' мин';
    }

    function renderBattery(b) {
        const level = Math.round(b.level * 100);
        $('batMeter').value = level;
        $('batLevel').textContent = level + '%';
        $('batCharging').textContent = b.charging ? 'заряжается (от сети)' : 'работает от батареи';
        $('batChargeTime').textContent = b.charging ? formatTime(b.chargingTime) : '—';
        $('batDischargeTime').textContent = b.charging ? '—' : formatTime(b.dischargingTime);
        batText = 'Заряд батареи ' + level + ' процентов, ' +
                  (b.charging ? 'устройство заряжается.' : 'устройство работает от батареи.');
    }

    if (batSupported) {
        navigator.getBattery().then((battery) => {
            $('batInfo').hidden = false;
            renderBattery(battery);
            ['levelchange', 'chargingchange', 'chargingtimechange', 'dischargingtimechange']
                .forEach((evt) => battery.addEventListener(evt, () => renderBattery(battery)));
            $('batSpeak').addEventListener('click', () => speak(batText));
        }).catch(() => {
            batMsg.textContent = 'Не удалось получить данные о батарее.';
        });
    } else {
        batMsg.textContent = 'Battery Status API не поддерживается этим браузером ' +
            '(работает в Chrome, Edge, Opera; в Safari и Firefox недоступен).';
    }
})();