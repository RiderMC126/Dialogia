document.getElementById('select-avatar-btn').addEventListener('click', function(event) {
    event.preventDefault(); // Отменяем стандартное поведение (отправку формы)
    document.getElementById('avatar-input').click();
});

// Добавляем обработчик, чтобы кнопка "Изменить аватар" была неактивна до выбора файла
document.getElementById('upload-avatar-btn').disabled = true;

document.getElementById('avatar-input').addEventListener('change', function() {
    console.log('Файл выбран:', this.files[0].name);
    document.getElementById('upload-avatar-btn').disabled = false;
});