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
            self.i = 0
            self.client.hset(self.user_id, 'news_i', self.i)
        else:
            i = int(self.client.hget(self.user_id, 'news_i').decode('utf-8'))
            if command[1] == '>':
                i += 1
            else:
                i-= 1
            i %= 5
            self.i = i
            self.client.hset(self.user_id, 'news_i', self.i)
        self.send_news()


    def send_news(self):
        params = {
            'country': 'ru',
            'apiKey': API_NEWS
        }
        response = requests.get('http://newsapi.org/v2/top-headlines?', params=params).json()['articles']
        result = []
        for elem in response[self.i * 4: self.i * 4 + 4]:
            result.append(elem['title'] + '\n' + elem['url'])
        self.client.hset(self.user_id, 'state', '!новости')
        keyboard = create_keyboard.create_keyboard(
            buttons=[['>', VkKeyboardColor.PRIMARY], ['<', VkKeyboardColor.PRIMARY]],
            inline=False)
        self.vk.messages.send(user_id=self.user_id,
                              message='\n\n'.join(result),
                              random_id=random.randint(0,
                                                       2 ** 64),
                              keyboard=keyboard)



