import calendar

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import datetime
import wikipedia
import requests
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from data.ideas import Ideas
import random

from data import db_session

DATETIME = {'01': "января", '02': "февраля", '03': "марта", '04': "апреля",
            '05': "мая", '06': "июня", '07': "июля", '08': "августа",
            '09': "сентября", '10': "октября", '11': "ноября", '12': "декабря"}
WEEK = {'0': 'понедельник', '1': 'вторник', '2': 'среда', '3': 'четверг',
        '4': 'пятница', '5': 'суббота', '6': 'воскресенье', }
URL = "https://translate.yandex.net/api/v1.5/tr.json/translate"
KEY = 'trnsl.1.1.20200326T112517Z.b892e6716bd0b2a8.fd91d2d249350b7b7642829f4d1a70a616d9fb3e'


def auth_handler():
    """ При двухфакторной аутентификации вызывается эта функция. """

    # Код двухфакторной аутентификации,
    # который присылается по смс или уведомлением в мобильное приложение
    key = input("Enter authentication code: ")
    # Если: True - сохранить, False - не сохранять.
    remember_device = True

    return key, remember_device


def create_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Привет', color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button('Котики', color=VkKeyboardColor.POSITIVE)
    return keyboard.get_keyboard()


def get_photo_id():
    login, password = LOGIN, PASSWORD
    vk_session = vk_api.VkApi(login, password, auth_handler=auth_handler)
    try:
        vk_session.auth(token_only=True)
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return
    vk = vk_session.get_api()
    photos = vk.photos.get(group_id=193402549, album_id=271476159)
    return photos


def translate_from_russian(mytext):
    params = {
        "key": KEY,
        "text": mytext,
        "lang": 'ru-en'
    }
    response = requests.get(URL, params=params)
    return response.json()['text'][0]


def translate_from_english(mytext):
    params = {
        "key": KEY,
        "text": mytext,
        "lang": 'en-ru'
    }
    response = requests.get(URL, params=params)
    return response.json()['text'][0]


def write_message(text, user_id, vk, attachment):
    vk.messages.send(user_id=user_id,
                     message=text,
                     random_id=random.randint(0, 2 ** 64), keyboard=create_keyboard(), attachment=attachment)


# def get_date(vk, user_id, text):
#     try:
#         date = calendar.weekday(int(text.split('.')[0]), int(text.split('.')[1]), int(text.split('.')[2]))
#         print(date)
#         vk.messages.send(user_id=user_id, message=f'Лови: {WEEK[str(date)]}',
#                          random_id=random.randint(0, 2 ** 64))
#     except Exception:
#         vk.messages.send(user_id=user_id, message=f'Я тебя не понимаю',
#                          random_id=random.randint(0, 2 ** 64))


def main():
    db_session.global_init("db/blogs.sqlite")
    print('ok')
    vk_session = vk_api.VkApi(
        token=TOKEN)
    longpoll = VkBotLongPoll(vk_session, '193402549')
    vk = vk_session.get_api()

    for event in longpoll.listen():
        if event.type == VkBotEventType.GROUP_JOIN:
            response = vk.users.get(user_id=event.obj['user_id'])
            vk.messages.send(user_id=event.obj['user_id'],
                             message=f'''{response[0]["first_name"]}!\nТебя приветствует бот
от проекта 2DYeS&#128526;\nС твоей помощью (да-да) я научусь делать все!!!\n(Ток подкинь идейку)&#128521;''',
                             random_id=random.randint(0, 2 ** 64))
        if event.type == VkBotEventType.MESSAGE_NEW:
            print(event)
            print('Новое сообщение:')
            print('Для меня от:', event.obj.message['from_id'])
            print('Текст:', event.obj.message['text'])
            text = event.obj.message['text'].lower()
            photo = random.choice(get_photo_id()['items'])
            response = vk.users.get(user_id=event.obj.message['from_id'],
                                    fields="bdate, city")
            if 'привет' in text:
                write_message(user_id=event.obj.message['from_id'], text=f'Привет, {response[0]["first_name"]}', vk=vk,
                              attachment=None)
            elif "котики" in text:
                write_message(user_id=event.obj.message['from_id'], text='Лови', vk=vk, attachment=f'photo{photo["owner_id"]}_{photo["id"]}')
            else:
                session = db_session.create_session()
                ideas = Ideas(
                    name=response[0]["first_name"] + ' ' + response[0]['last_name'],
                    idea=text
                )
                session.add(ideas)
                session.commit()
                write_message(user_id=event.obj.message['from_id'], text='Благодарю) Скоро будет готово&#128540;', vk=vk,
                              attachment=None)


if __name__ == '__main__':
    LOGIN, PASSWORD = '89372583764', 'житькайф'
    TOKEN = 'cc5ef7aff1765a84b162f4f94b94c39ddd63cc8cf61e7a08ebf19761be0c59a09c46cb9b3c07d179087d6'
    main()
