document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.getElementById('search-form');
    const cityInput = document.getElementById('city-input');
    const loader = document.getElementById('loader');
    const errorBox = document.getElementById('error-box');
    const errorText = document.getElementById('error-text');
    const contentArea = document.getElementById('content-area');

    const displayCity = document.getElementById('display-city');
    const displayDates = document.getElementById('display-dates');
    const weatherGrid = document.getElementById('weather-grid');
    const placesGrid = document.getElementById('places-grid');

    // Helper для визначення іконки погоди за текстом
    function getWeatherIcon(tempStr, precStr) {
        if (precStr.toLowerCase().includes('дощ') || precStr.toLowerCase().includes('rain')) return '🌧️';
        if (precStr.toLowerCase().includes('морос')) return '🌦️';
        if (precStr.toLowerCase().includes('сніг')) return '❄️';
        return '☀️';
    }

    async function fetchTravelData(city) {
        loader.classList.remove('hidden');
        errorBox.classList.add('hidden');
        contentArea.classList.add('hidden');

        try {
            const response = await fetch(`/api/travel?city=${encodeURIComponent(city)}`);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || "Не вдалося отримати дані");
            }

            renderDashboard(data);
        } catch (err) {
            errorText.textContent = err.message;
            errorBox.classList.remove('hidden');
        } finally {
            loader.classList.add('hidden');
        }
    }

    function renderDashboard(data) {
        displayCity.textContent = data.city.toUpperCase();
        displayDates.textContent = `${data.start_date} — ${data.end_date}`;

        // Очищаємо гріди
        weatherGrid.innerHTML = '';
        placesGrid.innerHTML = '';

        // Рендер погоди
        data.weather.forEach(day => {
            const icon = getWeatherIcon(day.formatted_temperature, day.formatted_precipitation);
            const card = document.createElement('div');
            card.className = 'glass-card weather-card';
            card.innerHTML = `
                <div class="day-date">${day.date}</div>
                <div class="weather-icon">${icon}</div>
                <div class="temp">${day.formatted_temperature}</div>
                <div class="prec">${day.formatted_precipitation}</div>
                <div class="wind">${day.formatted_wind}</div>
            `;
            weatherGrid.appendChild(card);
        });

        // Рендер пам'яток
        data.places.forEach((place, index) => {
            const card = document.createElement('div');
            card.className = 'glass-card place-card';
            card.innerHTML = `
                <div>
                    <div class="place-header">
                        <h4 class="place-title">${index + 1}. ${place.name}</h4>
                        <span class="place-badge">⭐ ${place.rating}</span>
                    </div>
                    <p class="place-desc">${place.description}</p>
                </div>
                <div class="place-footer">
                    <span>💬 Відгуків: ${place.reviews_count.toLocaleString()}</span>
                </div>
            `;
            placesGrid.appendChild(card);
        });

        contentArea.classList.remove('hidden');
    }

    // Обработка формы
    searchForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const city = cityInput.value.trim();
        if (city) {
            fetchTravelData(city);
        }
    });

    // Автоматично завантажуємо Київ при старті
    fetchTravelData('Kyiv');
});
