document.addEventListener('DOMContentLoaded', function() {
    const userInput = document.getElementById('user-input');
    const chatLog = document.querySelector('.chat-log');
    const sendButton = document.querySelector('.send-button');

    sendButton.addEventListener('click', function() {
        const userMessage = userInput.value.trim();
        if (userMessage) {
            // Добавляем сообщение пользователя в чат
            const userMessageHTML = `<div class="message user-message">${userMessage}</div>`;
            chatLog.innerHTML += userMessageHTML;

            // Отправляем ответ "Привет"
            const responseMessage = 'Привет';
            const responseMessageHTML = `<div class="message response-message">${responseMessage}</div>`;
            chatLog.innerHTML += responseMessageHTML;

            // Очищаем поле ввода
            userInput.value = '';

            // Прокручиваем чат в самый низ
            chatLog.scrollTop = chatLog.scrollHeight;
        }
    });

    // Если все же хотите использовать Enter
    userInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault(); // Предотвращаем стандартное поведение (перенос строки)
            sendButton.click(); // Симулируем клик на кнопку "Отправить"
        }
    });
});
