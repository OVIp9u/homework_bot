from pprint import pprint
import logging
import os
import time

import requests
import telegram
from telegram import ReplyKeyboardMarkup, Bot
from telegram.ext import CommandHandler, Updater
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv 

TELEGRAM_CHAT_ID = 490362590
TELEGRAM_TOKEN = '6279627909:AAEvjVT6AnsDNK419wcdcZ0SIXkN4l2xOD4'
bot = Bot(token=TELEGRAM_TOKEN)
homework_status_dict = {} #{'id':'status'}
homework_name_dict = {} #{'id':'lesson_name'}
response = {'homeworks': [
    {'id': 672168, 
    'status': 'approved', 
    'homework_name': 'OVIp9u__hw05_final.zip', 
    'reviewer_comment': 'Отлично! Есть пара некритичных моментов,глянь их обязательно', 
    'date_updated': '2023-02-16T12:50:46Z', 
    'lesson_name': 'Проект спринта: подписки на авторов'}, 
    {'id': 666069, 
    'status': 'approved', 
    'homework_name': 'OVIp9u__hw04_tests.zip', 
    'reviewer_comment': 'Супер!', 
    'date_updated': '2023-02-10T12:54:24Z', 
    'lesson_name': 'Проект спринта: покрытие тестами'}, 
    {'id': 652746, 'status': 'approved', 
    'homework_name': 'OVIp9u__hw03_forms.zip', 
    'reviewer_comment': 'Отлично!', 
    'date_updated': '2023-02-03T23:10:46Z', 
    'lesson_name': 'Проект спринта: новые записи'}, 
    {'id': 605064, 'status': 'approved', 
    'homework_name': 'OVIp9u__hw02_community.zip', 
    'reviewer_comment': 'Добрый день. Ошибка незначительная, можете исправить в следующем спринте', 
    'date_updated': '2023-01-17T19:19:32Z', 'lesson_name': 'Проект спринта: сообщества'}, 
    {'id': 573932, 'status': 'approved', 'homework_name': 'OVIp9u__hw_python_oop.zip', 
    'reviewer_comment': ' Поздравляю со сдачей работы. Успехов в дальнейшей учебе! ', 
    'date_updated': '2022-12-11T21:18:54Z', 'lesson_name': 'Проект спринта: модуль фитнес-трекера'}], 
    'current_date': 1678365749}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

def parse_status(response):
    """Извлекает из информации о конкретной домашней работе статус этой работы."""
    for homework in response['homeworks']:
        print(homework)
        if homework['id'] not in homework_status_dict.keys():
            homework_status_dict[homework['id']] = homework['status']
            homework_name_dict[homework['id']] = homework['lesson_name']
            homework_name = homework['lesson_name']
            verdict = HOMEWORK_VERDICTS[homework['status']]
            return f'Изменился статус проверки работы "{homework_name}". {verdict}'
        elif homework['status'] != homework_status_dict[homework['id']]:
            homework_status_dict[homework['id']] = homework['status']
            homework_name = homework['lesson_name']
            verdict = HOMEWORK_VERDICTS[homework['status']]
            return f'Изменился статус проверки работы "{homework_name}". {verdict}'
parse_status(response)