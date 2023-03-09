import logging
import os
import time
import sys
from pprint import pprint

import requests
import telegram
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Updater
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv 

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='program.log',
    level=logging.INFO)
# А тут установлены настройки логгера для текущего файла - example_for_log.py
logger = logging.getLogger(__name__)
# Устанавливаем уровень, с которого логи будут сохраняться в файл
logger.setLevel(logging.INFO)
# Указываем обработчик логов
handler = RotatingFileHandler('my_logger.log', maxBytes=50000000, backupCount=5)
logger.addHandler(handler)

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

TIMESTAMP = 0
homework_status_dict = {} #{'lesson_name':'status'}

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """проверяет доступность переменных окружения,
    которые необходимы для работы программы."""
    if not PRACTICUM_TOKEN:
        logger.critical('Отсутствует обязательная переменная окружения:"practicum_token"')
    elif not TELEGRAM_TOKEN:
        logger.critical('Отсутствует обязательная переменная окружения:"telegram_token"')
    elif not TELEGRAM_CHAT_ID:
        logger.critical('Отсутствует обязательная переменная окружения:"telegram_chat_id"')
    else:
        return True


def send_message(bot, message):
    """Функция send_message() отправляет сообщение в Telegram чат,
    определяемый переменной окружения TELEGRAM_CHAT_ID."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug('Сообщение отправлено')
    except:
        logging.error('Бот не смог отправить сообщение')
        raise requests.RequestException('Ошибка при отправке сообщения в чат.')


def get_api_answer(timestamp):
    """Делает запрос к эндпоинту API-сервиса."""
    logging.debug('Запрос к эндпоинту')
    try:
        homework_statuses = requests.get(ENDPOINT, headers=HEADERS, params={'from_date': timestamp})
        if homework_statuses.status_code != 200:
            raise requests.exceptions.RequestException('Ошибка статуса запроса.') 
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
    else:
        return print(homeworks)


def parse_status(homeworks):
    """Извлекает из информации о конкретной домашней работе статус этой работы."""
    for homework in homeworks:
        if homework['homework_name'] not in homework_status_dict.keys():
            homework_status_dict[homework['homework_name']] = homework['status']
            homework_name = homework['homework_name']
            verdict = HOMEWORK_VERDICTS[homework['status']]
            return f'Изменился статус проверки работы "{homework_name}". {verdict}'
        elif homework['status'] != homework_status_dict[homework['homework_name']]:
            homework_status_dict[homework['homework_name']] = homework['status']
            homework_name = homework['homework_name']
            verdict = HOMEWORK_VERDICTS[homework['status']]
            return f'Изменился статус проверки работы "{homework_name}". {verdict}'
        raise KeyError('Ошибка при проверки статуса работы.')


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        sys.exit('Отсутствует обязательная переменная окружения.')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    response = get_api_answer(TIMESTAMP)
    homeworks = check_response(response)
    message = parse_status(homeworks)
    send_message(bot, message)
    time.sleep(600)
    while True:
        try:
            send_message(bot, message)        
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
    

if __name__ == '__main__':
    main()

