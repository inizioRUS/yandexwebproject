from datetime import datetime
import random

import requests

from data.constants import *
from . import geobot
from . import helpbot
from . import create_keyboard
from . import weatherbot
from . import newsbot

COMMAND_DICT_BOT = {'!гео': geobot.GeoBot, '!помощь': helpbot.HelpBot, '!погода': weatherbot.WeatherBot, '!новости': newsbot.NewsBot}


class MainBot:
    def __init__(self, vk, user_id, client):
        self.vk = vk
        self.user_id = user_id
        self.client = client

    def analyse_type(self, message):
        if 'geo' in message:
            self.analyse_geolocation(message)
        elif message['attachments']:
            if 'sticker' in message['attachments'][0]:
                self.vk.messages.send(user_id=self.user_id,
                                      sticker_id=15131,
                                      random_id=random.randint(0, 2 ** 64))

        else:
            text = message['text'].lower().strip()
            self.analyse_text(text)

    def analyse_geolocation(self, message):
        lat, lon = message['geo']['coordinates'].values()
        self.client.hmset(self.user_id, {'geo': str(lon) + ',' + str(lat),
                                         "create_time": str(datetime.now())})
        self.client.hdel(self.user_id, 'state')
        keyboard = create_keyboard.create_keyboard(buttons=COMMAND_LIST,
                                                   inline=False, geo=True)
        self.vk.messages.send(user_id=self.user_id,
                              message=f'Геопозиция обновлена',
                              random_id=random.randint(0, 2 ** 64),
                              keyboard=keyboard)

    def analyse_text(self, text):
        if text == 'начать':
            self.start_text()
        elif text == 'вернуться на главную':
            self.come_back()
        else:
            state = self.client.hget(self.user_id, 'state')
            result = state.decode('utf-8') if state else ''
            if text.encode('unicode_escape').decode('utf-8')[0].isdigit():
                text = text.encode('unicode_escape').decode('utf-8')[0]
            result += ' ' + text
            result = result.strip()
            self.client.hset(self.user_id, 'state', result)
            command = result.split()[0]
            try:
                bot = COMMAND_DICT_BOT[command](self.vk, self.user_id,
                                                self.client, result)
                bot.analyse_command()

            except Exception as e:
                print(e)
                self.return_error('Команда не найдена. Попробуйте еще раз')

    def start_text(self):
        self.client.hdel(self.user_id, 'state')
        url = self.vk.photos.getMessagesUploadServer()

        response = requests.post(url=url['upload_url'],
                                 files={'photo': open('static/img/logo.jpg',
                                                      'rb')}).json()

        photo_info = self.vk.photos.saveMessagesPhoto(
            photo=response['photo'],
            server=response['server'],
            hash=response['hash'])[0]
        photo = f'photo{photo_info["owner_id"]}_{photo_info["id"]}'
        keyboard = create_keyboard.create_keyboard(
            buttons=COMMAND_LIST,
            inline=False, geo=True)
        self.vk.messages.send(user_id=self.user_id,
                              message=f'Проект 2DYeS представляет&#128526;\n\nГеобот - экосистема&#128202;, представляющий полный спектр услуг по вамешу местоположению\n\n\nОбо всех сложностях в работе писать админам&#128221;',
                              random_id=random.randint(0, 2 ** 64),
                              keyboard=keyboard, attachment=photo)

    def come_back(self):
        self.client.hdel(self.user_id, 'state')
        keyboard = create_keyboard.create_keyboard(
            buttons=COMMAND_LIST,
            inline=False, geo=True)
        self.vk.messages.send(user_id=self.user_id,
                              message=f'Выберите команду',
                              random_id=random.randint(0, 2 ** 64),
                              keyboard=keyboard)

    def return_error(self, error):
        self.client.hdel(self.user_id, 'state')
        keyboard = create_keyboard.create_keyboard(
            buttons=COMMAND_LIST,
            inline=False, geo=True)
        self.vk.messages.send(user_id=self.user_id,
                              message=error,
                              random_id=random.randint(0, 2 ** 64),
                              keyboard=keyboard)

