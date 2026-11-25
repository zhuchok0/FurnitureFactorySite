(function () {
    'use strict';

    const canvas = document.getElementById('seriesChart');
    if (!canvas) return;
    if (typeof Chart === 'undefined') {
        canvas.insertAdjacentHTML('afterend',
            '<p style="color:#d9534f">Chart.js не загрузился. Проверьте подключение скрипта.</p>');
        return;
    }

    const nInput = document.getElementById('seriesN');
    const nOutput = document.getElementById('seriesNValue');
    const drawBtn = document.getElementById('seriesDraw');
    const saveBtn = document.getElementById('seriesSave');
    const tbody = document.querySelector('#seriesTable tbody');

    const TABLE_X = [-0.9, -0.5, -0.2, 0, 0.2, 0.5, 0.9]; // значения x для таблицы
    const STEP = 0.05, X_MIN = -0.9, X_MAX = 0.9;

    // F(x) = sum_{k=1..n} (-1)^(k-1) * x^k / k
    function seriesLn(x, n) {
        let sum = 0;
        for (let k = 1; k <= n; k++) {
            sum += (k % 2 === 1 ? 1 : -1) * Math.pow(x, k) / k;
        }
        return sum;
    }

    function buildData(n) {
        const xs = [], series = [], exact = [];
        for (let x = X_MIN; x <= X_MAX + 1e-9; x += STEP) {
            const xr = Number(x.toFixed(2));
            xs.push(xr);
            series.push(seriesLn(xr, n));
            exact.push(Math.log(1 + xr));
        }
        return { xs, series, exact };
    }

    function fillTable(n) {
        tbody.innerHTML = '';
        TABLE_X.forEach((x) => {
            const f = seriesLn(x, n);
            const m = Math.log(1 + x);
            const tr = document.createElement('tr');
            [x, n, f.toFixed(6), m.toFixed(6), Math.abs(f - m).toExponential(3)].forEach((v) => {
                const td = document.createElement('td');
                td.textContent = v;
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });
    }

    // Белый фон, чтобы PNG не был прозрачным
    const whiteBackground = {
        id: 'whiteBackground',
        beforeDraw(chart) {
            const { ctx, width, height } = chart;
            ctx.save();
            ctx.globalCompositeOperation = 'destination-over';
            ctx.fillStyle = '#ffffff';
            ctx.fillRect(0, 0, width, height);
            ctx.restore();
        }
    };

    // Аннотация: текст и метка точки с максимальной погрешностью (попадает и в PNG)
    const annotation = {
        id: 'annotation',
        afterDatasetsDraw(chart) {
            const { ctx, chartArea: a, scales } = chart;
            const n = Number(nInput.value);
            const xs = chart.data.labels;
            let maxEps = 0, maxIdx = 0;
            chart.data.datasets[0].data.forEach((v, i) => {
                const e = Math.abs(v - chart.data.datasets[1].data[i]);
                if (e > maxEps) { maxEps = e; maxIdx = i; }
            });

            ctx.save();
            ctx.fillStyle = '#333';
            ctx.font = '14px Inter, sans-serif';
            ctx.textAlign = 'left';
            ctx.fillText('ln(1+x) = Σ (−1)^(k−1) · x^k / k,  |x| < 1', a.left + 12, a.top + 22);
            ctx.fillText('n = ' + n + ',  max eps = ' + maxEps.toExponential(2) +
                         ' при x = ' + xs[maxIdx], a.left + 12, a.top + 44);

            const px = scales.x.getPixelForValue(maxIdx);
            const py = scales.y.getPixelForValue(chart.data.datasets[0].data[maxIdx]);
            ctx.strokeStyle = '#d9534f';
            ctx.fillStyle = '#d9534f';
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.arc(px, py, 7, 0, Math.PI * 2);
            ctx.stroke();
            ctx.fillText('max eps', px + 12, py - 10);
            ctx.restore();
        }
    };

    let chart = null;

    // Анимация построения: точки появляются слева направо
    function progressiveAnimation(count, total) {
        const delay = (ctx) => (ctx.type === 'data' && ctx.mode === 'default' && !ctx.dropped)
            ? ctx.dataIndex * (total / count) : 0;
        const prevY = (ctx) => ctx.index === 0
            ? ctx.chart.scales.y.getPixelForValue(0)
            : ctx.chart.getDatasetMeta(ctx.datasetIndex).data[ctx.index - 1].getProps(['y'], true).y;
        return {
            x: { type: 'number', easing: 'linear', duration: total / count, from: NaN, delay },
            y: { type: 'number', easing: 'linear', duration: total / count, from: prevY, delay }
        };
    }

    function draw() {
        const n = Number(nInput.value);
        nOutput.textContent = n;
        const d = buildData(n);
        fillTable(n);

        if (chart) chart.destroy();

        chart = new Chart(canvas, {
            type: 'line',
            data: {
                labels: d.xs,
                datasets: [
                    {
                        label: 'F(x) — ряд, n = ' + n,
                        data: d.series,
                        borderColor: '#d9534f',
                        backgroundColor: '#d9534f',
                        borderWidth: 2.5,
                        pointRadius: 3,
                        tension: 0
                    },
                    {
                        label: 'Math F(x) = Math.log(1 + x)',
                        data: d.exact,
                        borderColor: '#2b7bd6',
                        backgroundColor: '#2b7bd6',
                        borderWidth: 2.5,
                        borderDash: [8, 5],
                        pointRadius: 0,
                        tension: 0
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animations: progressiveAnimation(d.xs.length, 1800),
                interaction: { mode: 'index', intersect: false },
                plugins: {
                    title: { display: true, text: 'Разложение ln(1+x) в степенной ряд', font: { size: 18 } },
                    legend: { display: true, position: 'bottom' },
                    tooltip: {
                        callbacks: {
                            afterBody(items) {
                                const i = items[0].dataIndex;
                                const e = Math.abs(chart.data.datasets[0].data[i] - chart.data.datasets[1].data[i]);
                                return 'eps = ' + e.toExponential(3);
                            }
                        }
                    }
                },
                scales: {
                    x: { title: { display: true, text: 'x' }, grid: { color: '#e5e5e5' } },
                    y: { title: { display: true, text: 'F(x)' }, grid: { color: '#e5e5e5' } }
                }
            },
            plugins: [whiteBackground, annotation]
        });
    }

    function save() {
        if (!chart) return;
        const link = document.createElement('a');
        link.href = chart.toBase64Image('image/png', 1);
        link.download = 'ln_series_n' + nInput.value + '.png';
        link.click();
    }

    nInput.addEventListener('input', () => { nOutput.textContent = nInput.value; });
    drawBtn.addEventListener('click', draw);
    saveBtn.addEventListener('click', save);

    draw();
})();