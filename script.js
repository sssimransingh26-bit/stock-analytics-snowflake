let chart = null;

function renderChart(data, symbol) {
    const labels = data.map(row => row.date).reverse();
    const prices = data.map(row => row.close).reverse();

    if (chart) chart.destroy();

    const ctx = document.getElementById('priceChart').getContext('2d');
    chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: `${symbol} Close Price`,
                data: prices,
                borderColor: '#00d4aa',
                backgroundColor: 'rgba(0, 212, 170, 0.1)',
                borderWidth: 2,
                pointRadius: 3,
                pointBackgroundColor: '#00d4aa',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: { color: '#ffffff' }
                }
            },
            scales: {
                x: {
                    ticks: { 
                        color: '#888',
                        maxTicksLimit: 10
                    },
                    grid: { color: '#2a2d3a' }
                },
                y: {
                    ticks: { 
                        color: '#888',
                        callback: value => `$${value}`
                    },
                    grid: { color: '#2a2d3a' }
                }
            }
        }
    });
}

async function loadStock(symbol) {
    symbol = symbol || document.getElementById('symbolInput').value.trim().toUpperCase();
    if (!symbol) return alert('Please enter a stock symbol');

    document.getElementById('tableBody').innerHTML = '<tr><td colspan="6" class="loading">Loading...</td></tr>';

    try {
        const analyticsRes = await fetch(`http://127.0.0.1:8000/stocks/${symbol}/analytics`);
        const analyticsData = await analyticsRes.json();

        if (analyticsData.detail) {
            document.getElementById('tableBody').innerHTML = `<tr><td colspan="6" class="loading">${analyticsData.detail}</td></tr>`;
            return;
        }

        const latest = analyticsData.analytics[0];
        if (!analyticsData.analytics || analyticsData.analytics.length === 0) {
    document.getElementById('tableBody').innerHTML = `<tr><td colspan="6" class="loading">No analytics data available.</td></tr>`;
    document.getElementById('closePrice').textContent = '--';
    document.getElementById('priceChange').textContent = '--';
    document.getElementById('percentChange').textContent = '--';
    document.getElementById('movingAvg').textContent = '--';
    return;
}
        document.getElementById('closePrice').textContent = `$${latest.close}`;

        const change = latest.price_change;
        const pct = latest.percent_change;
        const changeEl = document.getElementById('priceChange');
        changeEl.textContent = `$${change}`;
        changeEl.className = change >= 0 ? 'positive' : 'negative';
        document.getElementById('percentChange').textContent = `${pct}%`;
        document.getElementById('percentChange').className = `change ${pct >= 0 ? 'positive' : 'negative'}`;
        document.getElementById('movingAvg').textContent = latest.moving_avg_7day ? `$${latest.moving_avg_7day}` : '--';

        const stockRes = await fetch(`http://127.0.0.1:8000/stocks/${symbol}`);
        const stockData = await stockRes.json();

        if (stockData.detail) {
            document.getElementById('tableBody').innerHTML = `<tr><td colspan="6" class="loading">${stockData.detail}</td></tr>`;
            return;
        }

        const rows = stockData.data.map(row => `
            <tr>
                <td>${row.date}</td>
                <td>$${row.open}</td>
                <td>$${row.high}</td>
                <td>$${row.low}</td>
                <td>$${row.close}</td>
                <td>${row.volume.toLocaleString()}</td>
            </tr>
        `).join('');

        document.getElementById('tableBody').innerHTML = rows;
        
        renderChart(stockData.data, symbol);

    } catch (err) {
        document.getElementById('tableBody').innerHTML = '<tr><td colspan="6" class="loading">Error: ' + err.message + '</td></tr>';
    }
}

function selectTab(el, symbol) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    el.classList.add('active');
    document.getElementById('symbolInput').value = symbol;
    loadStock(symbol);
}

window.onload = () => loadStock('AAPL');
