document.addEventListener('DOMContentLoaded', function() {
  const categorySelect = document.getElementById('SelectCategory');
  const serviceSelect = document.getElementById('SelectService');
  const categoryContainerMini = document.querySelector('.category-id');
  const minQuantityText = document.querySelector('p.category-text:last-of-type');
  const quantityInput = document.getElementById('quantity');
  const displayQuantity = document.getElementById('display-quantity'); // Элемент для отображения количества
  const displayPrice = document.getElementById('display-price'); // Элемент для отображения цены
  const linkInput = document.getElementById('link'); // Элемент для ввода ссылки
  const createButton = document.querySelector('.create_button'); // Кнопка "Создать заказ"

  // Объект с вариантами услуг для каждой категории
  const servicesByCategory = {
    option1: [
      {
        id: 1,
        text: '⚡️ BOOST channel | 25-30 DAYS',
        price: 42,
        price_text: '42000₽ за 1000',
        description: 'ССЫЛКУ НУЖНО УКАЗЫВАТЬ НА САМ КАНАЛ<br>ССЫЛКА ДОЛЖНА БЫТЬ БЕЗ ЗАЯВОК<br><br>Бусты на закрытые и открытые каналы.<br>Буст держится 25-30 дней.<br>⚡️ Позволяет публиковать истории.<br>⭐ Личная база аккаунтов, прямой поставщик услуг.',
        minimum: 1,
        bt_id: 198
      },
      {
        id: 2,
        text: '⚡️ BOOST channel | 1 DAYS',
        price: 4,
        price_text: '4000₽ за 1000',
        description: 'ССЫЛКУ НУЖНО УКАЗЫВАТЬ НА САМ КАНАЛ<br>ССЫЛКА ДОЛЖНА БЫТЬ БЕЗ ЗАЯВОК<br><br>Бусты на закрытые и открытые каналы.<br>Буст держится 1 день.<br><br>⚡️ Позволяет публиковать истории.<br>⭐ Личная база аккаунтов, прямой поставщик услуг.',
        minimum: 1,
        bt_id: 181
      },
    ],
    option2: [
      {
        id: 3,
        text: '🤖 Premium BOT START MIX',
        price: 0.75,
        price_text: '750₽ за 1000',
        description: 'Запуск вашего бота с прем акаунтов.<br><br>NON DROP<br><br>Geo MIX',
        minimum: 1,
        bt_id: 205
      },
      {
        id: 4,
        text: '🤖 Premium BOT START RU',
        price: 8.5,
        price_text: '850₽ за 1000',
        description: 'Запуск вашего бота с прем акаунтов.<br><br>NON DROPE<br><br>Geo RU',
        minimum: 1,
        bt_id: 206
      },
      {
        id: 5,
        text: '🤖 BOT START RU',
        price: 0.2,
        price_text: '200₽ за 1000',
        description: 'Запуск вашего бота \n<br><br>аккаунт заходят без прем подписки\n<br><br>Geo RU',
        minimum: 1,
        bt_id: 207
      },
    ],
    option3: [
      {
        id: 6,
        text: '⭐️ 14+ days subscribers',
        price: 0.045,
        price_text: '45₽ за 1000',
        description: 'Ссылка должна быть указана на канал без заявок<br><br>Телеграм подписчики.<br>Отписки через 14+ дней<br>Моментальный запуск',
        minimum: 1,
        bt_id: 203
      },
      {
        id: 7,
        text: '⭐️ 30+ days subsrcibers',
        price: 0.08,
        price_text: '80₽ за 1000',
        description: 'Ссылка должна быть указана на канал без заявок<br><br>Телеграм подписчики.<br>Отписки через 30+ дней<br>Моментальный запуск',
        minimum: 1,
        bt_id: 204
      },
      {
        id: 8,
        text: '⭐️ 180+ days subsrcibers',
        price: 0.3,
        price_text: '300₽ за 1000',
        description: 'Без дропа минимум 180 дней!<br><br>🔍Подписчики присоединяются через поиск!<br><br>❤️ У 100% аккаунтов есть фотографии, имена соответствуют аватаркам.<br><br>Гео - МИКС.<br><br>Правила:<br>- Запрещенные каналы: наркотики, лохотрон, порно, пустые каналы.<br>- Каналы должны быть созданы более 2 недель!!!<br>- Должно быть минимум 3 поста на канале. Желательно в разные дни.<br>- Мы не гарантируем возврат средств за ГРУППЫ и ЧАТЫ с датой создания менее года назад.',
        minimum: 10,
        bt_id: 75
      },
    ],
    option4: [
      {
        id: 9,
        text: '👀 Просмотры на 50 постов',
        price: 0.25,
        price_text: '250₽ за 1000',
        description: 'Просмотры из России на последние 50 постов на канале.<br>Попадают в статистику.<br><br>Обратите внимание: если в постах присутствуют изображения, то каждое фото будет определено системой, как отдельный пост.',
        minimum: 100,
        bt_id: 166
      },
      {
        id: 10,
        text: '👀 Просмотры на 20 постов',
        price: 0.09,
        price_text: '90₽ за 1000',
        description: 'Просмотры из России на последние 20 постов на канале.<br>Попадают в статистику.<br><br>Обратите внимание: если в постах присутствуют изображения, то каждое фото будет определено системой, как отдельный пост.',
        minimum: 100,
        bt_id: 165
      },
      {
        id: 11,
        text: '👀 Просмотры на 10 постов',
        price: 0.045,
        price_text: '45₽ за 1000',
        description: 'Просмотры из России на последние 5 постов на канале.<br>Попадают в статистику.<br><br>Обратите внимание: если в постах присутствуют изображения, то каждое фото будет определено системой, как отдельный пост.',
        minimum: 100,
        bt_id: 164
      },
      {
        id: 12,
        text: '👀 Просмотры на 1 пост',
        price: 0.01,
        price_text: '10₽ за 1000',
        description: 'Указывать ссылку на пост.<br>Просмотры добавляются с русских ip адресов',
        minimum: 100,
        bt_id: 163
      },
    ],
  };

  // Добавить варианты для категории
  const categoryOptions = [
    { value: '', text: 'Выберите категорию' },
    { value: 'option1', text: 'Telegram Boost' },
    { value: 'option2', text: 'BOT /start' },
    { value: 'option3', text: 'Telegram Subscribers' },
    { value: 'option4', text: 'Telegram Views' },
  ];

  categoryOptions.forEach(function(option) {
    const categoryOption = document.createElement('option');
    categoryOption.value = option.value;
    categoryOption.text = option.text;
    if (option.value === '') {
      categoryOption.disabled = true;
      categoryOption.selected = true;
    }
    categorySelect.appendChild(categoryOption);
  });

  // Добавить пустой вариант для услуги
  const serviceOption = document.createElement('option');
  serviceOption.value = '';
  serviceOption.text = 'Выберите услугу';
  serviceOption.disabled = true;
  serviceOption.selected = true;
  serviceSelect.appendChild(serviceOption);

  // Функция для обновления количества и цены
  function updateQuantityAndPrice() {
    const selectedService = serviceSelect.value;
    const category = categorySelect.value;
    const quantity = parseInt(quantityInput.value, 10);

    if (selectedService && category) {
      const service = servicesByCategory[category].find(s => s.id === Number(selectedService));
      if (service) {
        const totalPrice = (service.price * quantity).toFixed(2); // Рассчитать цену
        displayQuantity.textContent = quantity; // Обновить количество
        displayPrice.textContent = `${totalPrice}₽`; // Обновить цену
      }
    }
  }

  // Обработчик события изменения категории
  categorySelect.addEventListener('change', function() {
    const selectedCategory = this.value;
    const services = servicesByCategory[selectedCategory];

    // Очистить текущие варианты услуг
    serviceSelect.innerHTML = '<option value="" disabled selected>Выберите услугу</option>';

    // Добавить новые варианты услуг
    if (services) {
      services.forEach(function(service) {
        const option = document.createElement('option');
        option.value = service.id; // Числовой ID
        option.text = service.text;
        serviceSelect.appendChild(option);
      });
    }

    // Обновить текст в .container-mini
    categoryContainerMini.innerHTML = `Категория: ${categorySelect.options[categorySelect.selectedIndex].text}`;

    // Сбросить минимальное количество
    minQuantityText.innerText = 'Минимальное количество: ';
    quantityInput.min = 1; // Сбросить минимальное значение ввода
    quantityInput.value = 1; // Сбросить значение ввода

    // Обновить количество и цену
    updateQuantityAndPrice();
  });

  // Обработчик события изменения услуги
  serviceSelect.addEventListener('change', function() {
    const selectedService = serviceSelect.value;
    const category = categorySelect.value;

    // Найти выбранную услугу
    const service = servicesByCategory[category].find(s => s.id === Number(selectedService));

    if (service) {
      // Обновить текст в .container-mini
      categoryContainerMini.innerHTML = `
        ID: ${service.id}<br>
        Категория: ${categorySelect.options[categorySelect.selectedIndex].text}<br>
        Услуга: ${service.text}<br>
        Цена: ${service.price_text}<br>
        Описание: <br></br>${service.description}
      `;

      // Обновить минимальное количество
      minQuantityText.innerText = `Минимальное количество: ${service.minimum}`;

      // Обновить атрибут min и значение ввода
      quantityInput.min = service.minimum;
      quantityInput.value = service.minimum; // Установить значение по умолчанию

      // Обновить количество и цену
      updateQuantityAndPrice();
    }
  });

  // Обработчик события изменения количества
  quantityInput.addEventListener('input', function() {
    updateQuantityAndPrice();
  });

  // Обработчик события для кнопки "Создать заказ"
  createButton.addEventListener('click', function() {
    const selectedService = serviceSelect.value;
    const category = categorySelect.value;
    const link = linkInput.value;
    const quantity = quantityInput.value;

    // Проверка, что все поля заполнены
    if (!selectedService || !category || !link || !quantity) {
      alert('Пожалуйста, заполните все поля.');
      return;
    }

    // Найти выбранную услугу
    const service = servicesByCategory[category].find(s => s.id === Number(selectedService));
    if (!service) {
      alert('Услуга не найдена.');
      return;
    }

    // Рассчитать общую стоимость
    const totalPrice = (service.price * quantity).toFixed(2);

    // Отправить данные на сервер
    fetch('/create_order', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        service_id: service.bt_id,
        link: link,
        quantity: quantity,
        price: totalPrice
      }),
    })
        .then(response => response.json())
        .then(data => {
          if (data.error) {
            alert(data.error);
          } else {
            console.log("Всё супер")
          }
        })
        .catch(error => {
          console.error('Ошибка:', error);
          alert('Произошла ошибка при отправке запроса.');
        });


    // Ваш API-ключ
    const apiKey = 'heJeyxWJLszVV2oAy4CPbcFOVWwXj14ZQoUZpYgbJfWHzDXMms5rMeAjKPrz'; // Замените на ваш реальный API-ключ

    // Формирование URL для запроса
    const apiUrl = `https://boosttelega.online/api/v2?action=add&service=${service.bt_id}&link=${encodeURIComponent(link)}&quantity=${quantity}&key=${apiKey}`;

    // Отправка запроса к API
    fetch(apiUrl)
      .then(response => response.json())
      .then(data => {
        if (data.order) {
          alert(`Заказ успешно создан! ID заказа: ${data.order}`);
        } else {
          alert('Ошибка при создании заказа. Пожалуйста, попробуйте снова.');
        }
      })
      .catch(error => {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при отправке запроса.');
      });
  });

  // Другой код для переключения контента
  const newOrderCard = document.getElementById('new-order');
  const allOrdersCard = document.getElementById('all-orders');
  const newOrderContent = document.getElementById('new-order-content');
  const allOrdersContent = document.getElementById('all-orders-content');

  newOrderCard.addEventListener('click', function() {
    newOrderContent.style.display = 'block';
    allOrdersContent.style.display = 'none';
  });

  allOrdersCard.addEventListener('click', function() {
    newOrderContent.style.display = 'none';
    allOrdersContent.style.display = 'block';
  });

  // Код для кнопки "API"
  const checkApiCard = document.getElementById('check-api');
  const apiContent = document.getElementById('api-content');

  checkApiCard.addEventListener('click', function() {
    // Скрыть другие контенты
    newOrderContent.style.display = 'none';
    allOrdersContent.style.display = 'none';

    // Показать контент для API
    apiContent.style.display = 'block';
  });
});

document.addEventListener('DOMContentLoaded', function() {
  const copyButton = document.querySelector('#copyableDiv img');

  copyButton.addEventListener('click', function(event) {
    event.stopPropagation(); // Чтобы не срабатывал обработчик клика на родительском элементе
    copyToClipboard(document.getElementById('copyableDiv'));
  });
});

function copyToClipboard(element) {
  const text = element.textContent;
  const textarea = document.createElement('textarea');
  textarea.value = text;
  textarea.setAttribute('readonly', '');
  textarea.style.position = 'absolute';
  textarea.style.left = '-9999px';
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand('copy');
  document.body.removeChild(textarea);
  alert('API-token скопирован в буфер обмена!');
}

