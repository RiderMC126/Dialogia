document.addEventListener('DOMContentLoaded', function() {
    const userInput = document.getElementById('user-input');
    const chatLog = document.getElementById('chat-log');
    const sendButton = document.getElementById('send-button');
    const clearButton = document.querySelector('button[name="clear-text"]');

    // Добавляем обработчик события для кнопки очистки
    clearButton.addEventListener('click', function() {
        chatLog.innerHTML = ''; // Очищаем лог чата
    });

    sendButton.addEventListener('click', function() {
        const userMessage = userInput.value.trim();
        if (userMessage) {
            // Добавляем сообщение пользователя в чат
            const userMessageHTML = `<div class="message user-message">${userMessage}</div>`;
            chatLog.innerHTML += userMessageHTML;
            // Прокручиваем чат в самый низ плавно
            chatLog.scrollTo({ top: chatLog.scrollHeight, behavior: 'smooth' });

            // Отправляем запрос на сервер
            fetch('/ai-chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `prompt=${encodeURIComponent(userMessage)}`,
            })
            .then(response => response.json())
            .then(data => {
                // Добавляем ответ ИИ в чат
                const responseMessageHTML = `<div class="message response-message">${data.answer}</div>`;
                chatLog.innerHTML += responseMessageHTML;

                // Прокручиваем чат в самый низ плавно
                chatLog.scrollTo({ top: chatLog.scrollHeight, behavior: 'smooth' });
            })
            .catch(error => {
                console.error('Ошибка:', error);
            });

            // Очищаем поле ввода
            userInput.value = '';
        }
    });

    // Обработка нажатия Enter
    userInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault(); // Предотвращаем стандартное поведение (перенос строки)
            sendButton.click(); // Симулируем клик на кнопку "Отправить"
        }
    });
});
