// tab.js

// Пример функции для обработки отправки формы и отображения рекомендации.
document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('.form');
    const recommendationsList = document.querySelector('.recommendations');

    form.addEventListener('submit', function(event) {
        event.preventDefault();
        
        // Получаем значение из текстового поля
        const preferences = document.getElementById('preferences').value;
        
        // Проверяем, есть ли введенные предпочтения
        if (preferences.trim() === '') {
            alert('Please enter your preferences!');
            return;
        }
        
        // Отправка данных на сервер и обновление списка рекомендаций
        // Можно добавить логику для работы с рекомендациями, если используется AJAX или другие запросы
        console.log('Preferences submitted:', preferences);
    });

    // Функция для отображения рекомендаций (если нужно обновлять список динамически)
    function displayRecommendations(recommendations) {
        recommendationsList.innerHTML = ''; // Очищаем текущий список

        recommendations.forEach(rec => {
            const listItem = document.createElement('li');
            listItem.innerHTML = `<strong>${rec.title}</strong> by ${rec.artist}`;
            recommendationsList.appendChild(listItem);
        });
    }
});
