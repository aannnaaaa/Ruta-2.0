document.addEventListener('DOMContentLoaded', function () {
    // Инициализация карты
    const map = L.map('map').setView([51.505, -0.09], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Обработчик клика по карте
    map.on('click', function (e) {
        document.getElementById('lat').value = e.latlng.lat;
        document.getElementById('lng').value = e.latlng.lng;
        L.marker([e.latlng.lat, e.latlng.lng]).addTo(map);
    });

    // Переключатель списка точек
    const toggleButton = document.getElementById('toggle-points');
    const pointsList = document.getElementById('points-list');
    toggleButton.addEventListener('click', function () {
        pointsList.style.display = pointsList.style.display === 'none' ? 'block' : 'none';
    });
});