document.addEventListener('DOMContentLoaded', function() {
  const categorySelect = document.getElementById('SelectCategory');
  const serviceSelect = document.getElementById('SelectService');
  const categoryContainerMini = document.querySelector('.category-id');
  const minQuantityText = document.querySelector('p.category-text:last-of-type');
  const quantityInput = document.getElementById('quantity');
  const displayQuantity = document.getElementById('display-quantity'); // Элемент для отображения количества
  const displayPrice = document.getElementById('display-price'); // Элемент для отображения цены

  // Объект с вариантами услуг для каждой категории
  const servicesByCategory = {
    option1: [
      {
        id: 1,
        text: '⚡️ BOOST channel | 25-30 DAYS',
        price: 42,
        price_text: '42000₽ за 1000',
        description: 'Услуга по накрутке канала в Telegram на 25-30 дней.',
        minimum: 1
      },
      {
        id: 2,
        text: '⚡️ BOOST channel | 1 DAYS',
        price: 4,
        price_text: '4000₽ за 1000',
        description: 'Услуга по накрутке канала в Telegram на 1 день.',
        minimum: 1
      },
    ],
    option2: [
      {
        id: 3,
        text: '🤖 Premium BOT START MIX',
        price: 0.75,
        price_text: '750₽ за 1000',
        description: 'Премиум-услуга по запуску бота с миксом.',
        minimum: 1
      },
      {
        id: 4,
        text: '🤖 Premium BOT START RU',
        price: 8.5,
        price_text: '850₽ за 1000',
        description: 'Премиум-услуга по запуску бота для России.',
        minimum: 1
      },
      {
        id: 5,
        text: '🤖 BOT START RU',
        price: 0.2,
        price_text: '200₽ за 1000',
        description: 'Услуга по запуску бота для России.',
        minimum: 1
      },
    ],
    option3: [
      {
        id: 6,
        text: '⭐️ 14+ days subscribers',
        price: 0.045,
        price_text: '45₽ за 1000',
        description: 'Услуга по привлечению подписчиков на 14+ дней.',
        minimum: 1
      },
      {
        id: 7,
        text: '⭐️ 30+ days subsrcibers',
        price: 0.08,
        price_text: '80₽ за 1000',
        description: 'Услуга по привлечению подписчиков на 30+ дней.',
        minimum: 1
      },
      {
        id: 8,
        text: '⭐️ 180+ days subsrcibers',
        price: 0.3,
        price_text: '300₽ за 1000',
        description: 'Услуга по привлечению подписчиков на 180+ дней.',
        minimum: 10
      },
    ],
    option4: [
      {
        id: 9,
        text: '👀 Просмотры на 50 постов',
        price: 0.25,
        price_text: '250₽ за 1000',
        description: 'Услуга по увеличению просмотров на 50 постов.',
        minimum: 100
      },
      {
        id: 10,
        text: '👀 Просмотры на 20 постов',
        price: 0.09,
        price_text: '90₽ за 1000',
        description: 'Услуга по увеличению просмотров на 20 постов.',
        minimum: 100
      },
      {
        id: 11,
        text: '👀 Просмотры на 10 постов',
        price: 0.045,
        price_text: '45₽ за 1000',
        description: 'Услуга по увеличению просмотров на 20 постов.',
        minimum: 100
      },
      {
        id: 12,
        text: '👀 Просмотры на 1 пост',
        price: 0.01,
        price_text: '10₽ за 1000',
        description: 'Услуга по увеличению просмотров на 1 пост.',
        minimum: 100
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
        Категория: ${categorySelect.options[categorySelect.selectedIndex].text}<br>
        Услуга: ${service.text}<br>
        Цена: ${service.price_text}<br>
        Описание: ${service.description}<br>
        ID: ${service.id}
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
});