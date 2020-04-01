import calendar

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import datetime
import wikipedia
import requests
from data.geolocation import GeoLocation
import random

from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from data import db_session

DATETIME = {'01': "января", '02': "февраля", '03': "марта", '04': "апреля",
            '05': "мая", '06': "июня", '07': "июля", '08': "августа",
            '09': "сентября", '10': "октября", '11': "ноября", '12': "декабря"}
WEEK = {'0': 'понедельник', '1': 'вторник', '2': 'среда', '3': 'четверг',
        '4': 'пятница', '5': 'суббота', '6': 'воскресенье', }
URL = "https://translate.yandex.net/api/v1.5/tr.json/translate"
KEY_TRANSLATE = 'trnsl.1.1.20200326T112517Z.b892e6716bd0b2a8.fd91d2d249350b7b7642829f4d1a70a616d9fb3e'
COMMAND_DICT = {
    'geolocation': {'help': '',
                    'categories': [['продукты', VkKeyboardColor.PRIMARY],
                                   ['метро', VkKeyboardColor.PRIMARY],
                                   ['аптека', VkKeyboardColor.PRIMARY]]}}
COMMAND_LIST = [['!Помощь', VkKeyboardColor.POSITIVE],
                ['!Гео', VkKeyboardColor.DEFAULT]]
NUMBERS = [['1', VkKeyboardColor.PRIMARY], ['2', VkKeyboardColor.PRIMARY],
           ['3', VkKeyboardColor.PRIMARY], ['4', VkKeyboardColor.PRIMARY],
           ['5', VkKeyboardColor.PRIMARY]]


def auth_handler():
    """ При двухфакторной аутентификации вызывается эта функция. """

    # Код двухфакторной аутентификации,
    # который присылается по смс или уведомлением в мобильное приложение
    key = input("Enter authentication code: ")
    # Если: True - сохранить, False - не сохранять.
    remember_device = True

    return key, remember_device


# def get_photo_id():
#     login, password = LOGIN, PASSWORD
#     vk_session = vk_api.VkApi(login, password, auth_handler=auth_handler)
#     try:
#         vk_session.auth(token_only=True)
#     except vk_api.AuthError as error_msg:
#         print(error_msg)
#         return
#     vk = vk_session.get_api()
#     photos = vk.photos.get(group_id=193402549, album_id=271476159)
#     return photos

def set_centr(coor_1, coor_2):
    x1, y1 = map(float, coor_1.split(','))
    x2, y2 = map(float, coor_2.split(','))
    return [str((x1 + x2) / 2), str((y1 + y2) / 2)]


def create_keyboard(command=None, buttons=None, inline=False, location=False):
    keyboard = VkKeyboard(one_time=False, inline=inline)
    if not location:
        i = 0
        for i in range(len(buttons) // 2):
            for j in range(2):
                keyboard.add_button(command + buttons[i * 2 + j][0],
                                    color=buttons[i * 2 + j][1])
            keyboard.add_line()
        for i in range(len(buttons) % 2):
            keyboard.add_button(command + buttons[- i - 1][0],
                                color=buttons[- i - 1][1])
        keyboard.add_button('Вернуться на главную',
                            color=VkKeyboardColor.NEGATIVE)
    else:
        keyboard.add_location_button()

    return keyboard.get_keyboard()


def list_objects(address_ll, obj):
    search_api_server = "https://search-maps.yandex.ru/v1/"
    api_key = 'dda3ddba-c9ea-4ead-9010-f43fbc15c6e3'
    search_params = {
        "apikey": api_key,
        "text": obj,
        "lang": "ru_RU",
        "ll": address_ll,
        "type": "biz"
    }
    response = requests.get(search_api_server, params=search_params)
    json_response = response.json()
    return '\n'.join(
        [str(i + 1) + '. ' + json_response["features"][i]['properties'][
            'name'] + ' ' +
         json_response["features"][i]['properties']['description']
         for i in range(5)])


def get_map(address_ll, obj, i):
    search_api_server = "https://search-maps.yandex.ru/v1/"
    api_key = 'dda3ddba-c9ea-4ead-9010-f43fbc15c6e3'
    search_params = {
        "apikey": api_key,
        "text": obj,
        "lang": "ru_RU",
        "ll": address_ll,
        "type": "biz"
    }
    response = requests.get(search_api_server, params=search_params)
    json_response = response.json()
    obj_ll = ','.join(list(
        map(str, json_response['features'][i]['geometry']['coordinates'])))
    centr = ','.join(set_centr(address_ll, obj_ll))
    map_request = f"http://static-maps.yandex.ru/1.x/"
    params = {
        'll': centr,
        'l': 'map',
        'pt': '~'.join([address_ll + ',ya_ru', obj_ll + ',comma'])
    }
    response = requests.get(map_request, params=params)
    return response.content



def translate_from_russian(mytext):
    params = {
        "key": KEY_TRANSLATE,
        "text": mytext,
        "lang": 'ru-en'
    }
    response = requests.get(URL, params=params)
    return response.json()['text'][0]


def translate_from_english(mytext):
    params = {
        "key": KEY_TRANSLATE,
        "text": mytext,
        "lang": 'en-ru'
    }
    response = requests.get(URL, params=params)
    return response.json()['text'][0]


def command_handler(vk, user_id, command):
    if command.startswith('гео'):
        geolocation(vk, user_id, command)

    elif command.startswith('помощь'):
        pass


def geolocation(vk, user_id, command):
    session = db_session.create_session()
    geoloc = session.query(GeoLocation).filter(
        GeoLocation.user_id == user_id).all()
    if geoloc:
        geoloc = geoloc[-1]
        delta_time = str(datetime.datetime.now() - geoloc.create_time).split()
        if delta_time[0].split(':')[0] == '0':
            command = command.split()
            if len(command) == 1:
                keyboard = create_keyboard(command='!Гео ',
                                           buttons=COMMAND_DICT['geolocation'][
                                               'categories'], inline=False)

                vk.messages.send(user_id=user_id,
                                 message=f'Выберите категорию',
                                 random_id=random.randint(0, 2 ** 64),
                                 keyboard=keyboard)
            elif len(command) == 2:
                objects = list_objects(geoloc.geo, command[1])
                keyboard = create_keyboard(command='!Гео ' + command[1] + ' ',
                                           buttons=NUMBERS,
                                           inline=False)

                vk.messages.send(user_id=user_id,
                                 message=f'Выберите объект\n' + objects,
                                 random_id=random.randint(0, 2 ** 64),
                                 keyboard=keyboard)
            elif len(command) == 3:
                map = get_map(geoloc.geo, command[1], int(command[2]))
                map_file = "map.png"
                with open(map_file, "wb") as file:
                    file.write(map)


        else:
            keyboard = create_keyboard(inline=True, location=True)

            vk.messages.send(user_id=user_id, message=f'Обновите геопозицию',
                             random_id=random.randint(0, 2 ** 64),
                             keyboard=keyboard)
    else:
        keyboard = create_keyboard(inline=True, location=True)

        vk.messages.send(user_id=user_id, message=f'Обновите геопозицию',
                         random_id=random.randint(0, 2 ** 64),
                         keyboard=keyboard)


def get_date(vk, user_id, text):
    try:
        date = calendar.weekday(int(text.split('.')[0]),
                                int(text.split('.')[1]),
                                int(text.split('.')[2]))
        print(date)
        vk.messages.send(user_id=user_id, message=f'Лови: {WEEK[str(date)]}',
                         random_id=random.randint(0, 2 ** 64))
    except Exception:
        vk.messages.send(user_id=user_id, message=f'Я тебя не понимаю',
                         random_id=random.randint(0, 2 ** 64))


def main():
    db_session.global_init("db/blogs.sqlite")
    print('----------------------------------------------------------')
    session = db_session.create_session()
    vk_session = vk_api.VkApi(
        token=TOKEN)
    longpoll = VkBotLongPoll(vk_session, '193402549')
    vk = vk_session.get_api()

    for event in longpoll.listen():
        if event.type == VkBotEventType.GROUP_JOIN:
            response = vk.users.get(user_id=event.obj['user_id'])
            vk.messages.send(user_id=event.obj['user_id'],
                             message=f'''Привет, {response[0]["first_name"]}\nЯ
                              бот от проекта 2DYeS\nНапиши /help чтобы
                               узнать, что я умею''',
                             random_id=random.randint(0, 2 ** 64))
        if event.type == VkBotEventType.MESSAGE_NEW:

            print('Новое сообщение:')
            print('Для меня от:', event.obj.message['from_id'])
            user_id = event.obj.message['from_id']
            print('Текст:', event.obj.message['text'])
            print('----------------------------------------------------------')
            if 'geo' in event.obj.message:
                lat, lon = event.obj.message['geo']['coordinates'].values()
                geo = GeoLocation(
                    user_id=user_id,
                    geo=str(lon) + ',' + str(lat),
                    create_time=datetime.datetime.now()
                )
                session.add(geo)
                session.commit()
                keyboard = create_keyboard(command='', buttons=COMMAND_LIST,
                                           inline=False)
                vk.messages.send(user_id=user_id,
                                 message=f'Геопозиция обновлена',
                                 random_id=random.randint(0, 2 ** 64),
                                 keyboard=keyboard)
            else:
                text = event.obj.message['text'].lower().strip()
                if text == 'начать':
                    keyboard = create_keyboard(command='',
                                               buttons=COMMAND_LIST,
                                               inline=False)
                    vk.messages.send(user_id=user_id,
                                     message=f'Выберите команду',
                                     random_id=random.randint(0, 2 ** 64),
                                     keyboard=keyboard)
                elif text == 'вернуться на главную':
                    keyboard = create_keyboard(command='',
                                               buttons=COMMAND_LIST,
                                               inline=False)
                    vk.messages.send(user_id=user_id,
                                     message=f'Выберите команду',
                                     random_id=random.randint(0, 2 ** 64),
                                     keyboard=keyboard)
                elif text.startswith('!'):
                    command_handler(vk, user_id, text[1:])

            # response = vk.users.get(user_id=event.obj.message['from_id'],
            #                         fields="bdate, city")


if __name__ == '__main__':
    TOKEN = '59bee4154449bd32baddc0d47420e6dfaf633c482a5b7cddf2c4aab118c1b10e442b425cb3f1e4b33d4de'
    main()
