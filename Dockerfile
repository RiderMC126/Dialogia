#FROM ubuntu:latest
#LABEL authors="markp"
#
#ENTRYPOINT ["top", "-b"]

# Используем базовый образ Python
FROM python:3.13

# Установка рабочей директории
WORKDIR /app

# Копируем файл requirements.txt
COPY requirements.txt .

# Установка зависимостей
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

# Копируем остальные файлы приложения
COPY . .

# Запускаем приложение
CMD ["python", "main.py"]
