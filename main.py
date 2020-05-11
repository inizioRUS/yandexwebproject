import redis
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import logging

import requests

import random
from config import *

from data import mainbot

logging.basicConfig(level=logging.INFO)


def auth_handler():
    """ При двухфакторной аутентификации вызывается эта функция. """

    # Код двухфакторной аутентификации,
    # который присылается по смс или уведомлением в мобильное приложение
    key = input("Enter authentication code: ")
    # Если: True - сохранить, False - не сохранять.
    remember_device = True

    return key, remember_device


def main():
    print('----------------------------------------------------------')
    vk_session = vk_api.VkApi(
        token=TOKEN)
    longpoll = VkBotLongPoll(vk_session, GROUP_ID)

    print('ok')
    vk = vk_session.get_api()
    client = redis.Redis()
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            print('Новое сообщение:')
            print('Для меня от:', event.obj.message['from_id'])
            print('Текст:', event.obj.message['text'])
            print('----------------------------------------------------------')

            mainbot_ = mainbot.MainBot(vk, event.obj.message['from_id'],
                                       client)
            mainbot_.analyse_type(event.obj.message)
            print('ok')



if __name__ == '__main__':
    main()
