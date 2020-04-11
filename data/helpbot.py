import random
from datetime import datetime

import requests
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from .constants import *
from . import create_keyboard


class HelpBot:
    def __init__(self, vk, user_id, client, command):
        self.vk = vk
        self.user_id = user_id
        self.client = client
        self.command = command

    def analyse_command(self):
        command = self.command.split()
        if len(command) == 1:
            self.choose_help()
        elif len(command) == 2:
            self.send_help(command[1])
        else:
            self.not_found_command()

    def choose_help(self):
        keyboard = create_keyboard.create_keyboard(
            buttons=HELP_LIST,
            inline=False)
        self.vk.messages.send(user_id=self.user_id,
                              message=f'Выберите раздел',
                              random_id=random.randint(0, 2 ** 64),
                              keyboard=keyboard)

    def send_help(self, command):
        if '!' + command not in COMMAND_DICT:
            return self.not_found_command()
        keyboard = create_keyboard.create_keyboard(
            buttons=COMMAND_LIST,
            inline=False, geo=True)
        self.client.hdel(self.user_id, 'state')
        self.vk.messages.send(user_id=self.user_id,
                              message=COMMAND_DICT['!' + command]['помощь'],
                              random_id=random.randint(0,
                                                       2 ** 64),
                              keyboard=keyboard)

    def not_found_command(self):
        keyboard = create_keyboard.create_keyboard(
            buttons=COMMAND_LIST,
            inline=False, geo=True)
        self.client.hdel(self.user_id, 'state')
        self.vk.messages.send(user_id=self.user_id,
                              message='Команда не найдена',
                              random_id=random.randint(0,
                                                       2 ** 64),
                              keyboard=keyboard)
