document.addEventListener('DOMContentLoaded', function() {
    const compareBtn = document.querySelector('#compare-btn');
    const city1Input = document.querySelector('#city1');
    const city2Input = document.querySelector('#city2');
    const comparisonSection = document.querySelector('#comparison-result');
    const summaryText = document.querySelector('#summary-text');

    compareBtn.addEventListener('click', async function() {
        const city1 = city1Input.value.trim();
        const city2 = city2Input.value.trim();

        if (!city1 || !city2) {
            alert('请同时输入两个城市名称');
            return;
        }

        try {
            compareBtn.disabled = true;
            compareBtn.textContent = '查询中...';

            const response = await fetch('/get_weather', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ city1, city2 })
            });

            const data = await response.json();

            if (!response.ok || data.error) {
                const msg = data && data.error ? data.error : '接口返回异常';
                throw new Error(msg);
            }

            // 天气卡片渲染
            updateWeatherDisplay(data.city1, document.querySelector('#city1-weather .weather-info'));
            updateWeatherDisplay(data.city2, document.querySelector('#city2-weather .weather-info'));

            // 概述
            summaryText.textContent = data.summary || '';

            // 详细对比列表
            const live1 = data.city1.lives[0];
            const live2 = data.city2.lives[0];
            comparisonSection.innerHTML = `
                <div class="comparison-header">
                    <div class="cities-compared">
                        <strong>${live1.city}</strong> vs <strong>${live2.city}</strong>
                    </div>
                </div>
                <ul>
                    ${data.comparison.map(item => `<li>${item}</li>`).join('')}
                </ul>
            `;
        } catch (error) {
            console.error('Error:', error);
            alert('获取天气失败：' + error.message);
        } finally {
            compareBtn.disabled = false;
            compareBtn.textContent = '开始对比';
        }
    });

    function updateWeatherDisplay(weatherData, container) {
        const live = weatherData.lives[0];
        container.innerHTML = `
            <h3>${live.city}</h3>
            <div class="temperature">${live.temperature}°C</div>
            <div class="weather-details">
                <p><strong>天气：</strong> ${live.weather}</p>
                <p><strong>湿度：</strong> ${live.humidity}%</p>
                <p><strong>风：</strong> ${live.winddirection} ${live.windpower}</p>
                <p><strong>发布时间：</strong> ${live.reporttime}</p>
            </div>
        `;
    }
});
