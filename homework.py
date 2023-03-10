import logging
import os
import sys
import time
from logging.handlers import RotatingFileHandler

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='program.log',
    level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(
    'my_logger.log',
    maxBytes=50000000,
    backupCount=5
)

logger.addHandler(handler)

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

TIMESTAMP = 0

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверяет доступность переменных окружения."""
    if not PRACTICUM_TOKEN:
        logger.critical('Отсутствует переменная окружения:"practicum_token"')
    elif not TELEGRAM_TOKEN:
        logger.critical('Отсутствует переменная окружения:"telegram_token"')
    elif not TELEGRAM_CHAT_ID:
        logger.critical('Отсутствует переменная окружения:"telegram_chat_id"')
    else:
        return True


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug('Сообщение отправлено')
    except logging.error('Бот не смог отправить сообщение'):
        raise requests.RequestException('Ошибка при отправке сообщения в чат.')


def get_api_answer(timestamp):
    """Делает запрос к эндпоинту API-сервиса."""
    logging.debug('Запрос к эндпоинту')
    try:
        homework_statuses = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params={'from_date': timestamp}
        )
        if homework_statuses.status_code != 200:
            raise requests.exceptions.RequestException(
                'Ошибка статуса запроса.'
            )
        else:
            response = homework_statuses.json()
            return response
    except requests.exceptions.RequestException as error:
        raise Exception(f'Ошибка при запросе к API: {error}')


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    if type(response) != dict:
        raise TypeError('Ответ не является словарем')
    if 'homeworks' not in response:
        logging.error('Ключ "homeworks" отсутствует в ответе')
        raise KeyError('Ключ "homeworks" отсутствует в ответе')
    homeworks = response['homeworks']
    if type(homeworks) != list:
        raise TypeError('Ответ по ключу "homework" не является списком')
    elif 'current_date' not in response:
        raise KeyError('Ключ "current_date" отсутствует в ответе')
    elif homeworks is None:
        raise ValueError('Homework is NoneType')
    elif homeworks == []:
        return None
    else:
        return homeworks[0]


def parse_status(homework):
    """Извлекает из информации о статусе работы."""
    if homework is None:
        return None
    elif 'homework_name' not in homework:
        raise ValueError('В данных отсутствует ключ: homework_name')
    elif 'status' not in homework:
        raise ValueError('В данных отсутствует ключ: status')
    elif homework['status'] not in HOMEWORK_VERDICTS:
        raise ValueError('Неправильный статус')
    try:
        homework_name = homework['homework_name']
        homework_status = homework['status']
        verdict = HOMEWORK_VERDICTS[homework_status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    except requests.exceptions.RequestException as error:
        raise Exception(f'Ошибка в данных: {error}')


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        sys.exit('Отсутствует обязательная переменная окружения.')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    response = get_api_answer(TIMESTAMP)
    homework = check_response(response)
    previous_message = parse_status(homework)
    send_message(bot, previous_message)
    time.sleep(600)
    while True:
        try:
            response = get_api_answer(TIMESTAMP)
            homework = check_response(response)
            new_message = parse_status(homework)
            if new_message != previous_message:
                send_message(bot, new_message)
                previous_message = new_message
        except Exception as error:
            error_message = f'Сбой в работе программы: {error}'
            send_message(bot, error_message)


if __name__ == '__main__':
    main()
