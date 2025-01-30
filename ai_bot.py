import random
import logging
from enum import Enum
from g4f.client import Client

# Настройка логгера
logger = logging.getLogger("AI_Request")
logger.setLevel(logging.DEBUG)


# Модели ИИ
class G4FModels(Enum):
    GPT4_MINI = "gpt-4"
    LLAMA3_1 = "llama-3.1-70b"
    SONNET = "claude-3.5-sonnet"


# Клиент для работы с ИИ
client = Client()


def log(text: str) -> None:
    """Логирование сообщений."""
    logger.info(text)


def generate_response(prompt: str, max_attempts: int = 5) -> str:
    """
    Генерирует ответ на основе запроса (prompt) с использованием случайной модели ИИ.

    :param prompt: Текст запроса.
    :param max_attempts: Максимальное количество попыток.
    :return: Сгенерированный ответ.
    """
    models = list(G4FModels)
    for attempt in range(max_attempts):
        model = random.choice(models)
        try:
            log(f"Попытка {attempt + 1}: Используем модель {model.value}")
            response = client.chat.completions.create(
                model=model.value,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            content = response.choices[0].message.content
            log(f"Ответ от модели {model.value}: {content}")
            return content
        except Exception as e:
            logger.error(f"Ошибка в попытке {attempt + 1}: {e}")
    return ""


# Пример использования
if __name__ == "__main__":
    prompt = "Привет, как дела?"
    response = generate_response(prompt)
    print("Ответ от ИИ:", response)