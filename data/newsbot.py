import calendar
import random
from datetime import datetime
from config import *
import requests
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from .constants import *
from . import create_keyboard


class NewsBot:
    def __init__(self, vk, user_id, client, command):
        self.vk = vk
        self.user_id = user_id
        self.client = client
        self.command = command

    def analyse_command(self):
        command = self.command.split()
        if len(command) == 1:
            self.choose_news()
        else:
            pass
            self.send_news(' '.join(command[1:]))

    def choose_news(self):
        keyboard = create_keyboard.create_keyboard(buttons=
                                                   COMMAND_DICT['!новости'][
                                                       'категории'],
                                                   inline=False, d=2)

        self.vk.messages.send(user_id=self.user_id,
                              message=f'Выберите категорию',
                              random_id=random.randint(0, 2 ** 64),
                              keyboard=keyboard)

    def send_news(self, search):
        search_list = NEWS[search]
        result = []
        response = requests.get('https://api.lenta.ru/')
        while '404' in str(response):
            response = requests.get('https://api.lenta.ru/')
        response = response.json()
        for new in response['top7']:
            for label in new['labels']:
                if label['name'].lower() in search_list:
                    result.append(f"{new['title']}&#128240;\n{new['announce']}")
                    break
        self.client.hdel(self.user_id, 'state')
        keyboard = create_keyboard.create_keyboard(
            buttons=COMMAND_LIST,
            inline=False, geo=True)
        if result:
            self.vk.messages.send(user_id=self.user_id,
                              message='\n\n'.join(result),
                              random_id=random.randint(0,
                                                       2 ** 64),
                              keyboard=keyboard)
        else:
            self.vk.messages.send(user_id=self.user_id,
                                  message='В настоящий момент актуальных новостей на эту тему нет',
                                  random_id=random.randint(0,
                                                           2 ** 64),
                                  keyboard=keyboard)

