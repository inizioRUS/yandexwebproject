import random
from datetime import datetime
from config import *
import requests
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from .constants import *
from . import create_keyboard


class GeoBot:
    def __init__(self, vk, user_id, client, command):
        self.vk = vk
        self.user_id = user_id
        self.client = client
        self.command = command

    def analyse_command(self):
        geo = self.client.hget(self.user_id, 'geo')

        if geo:
            time = self.client.hget(self.user_id, 'create_time').decode(
                'utf-8').split('.')[0]
            time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
            delta_time = str(
                datetime.now() - time).split()
            if delta_time[0].split(':')[0] == '0':
                command = self.command.split()
                if len(command) == 1:
                    self.choose_catetgories()
                else:
                    if not command[-1][-1].isdigit():
                        self.choose_number(geo.decode('utf-8'), command[1:])
                    else:
                        self.send_map(geo.decode('utf-8'), command[1:-1],
                                      int(command[-1]))
            else:
                self.wrong_geolocation()
        else:
            self.wrong_geolocation()

    def wrong_geolocation(self):
        keyboard = create_keyboard.create_keyboard(inline=True, location=True)
        self.vk.messages.send(user_id=self.user_id,
                              message=f'Обновите геопозицию',
                              random_id=random.randint(0, 2 ** 64),
                              keyboard=keyboard)

    def choose_catetgories(self):
        keyboard = create_keyboard.create_keyboard(buttons=
                                                   COMMAND_DICT['!гео'][
                                                       'категории'],
                                                   inline=False)

        self.vk.messages.send(user_id=self.user_id,
                              message=f'Выберите категорию',
                              random_id=random.randint(0, 2 ** 64),
                              keyboard=keyboard)

    def get_list_of_objects(self, address_ll, obj):
        search_api_server = "https://search-maps.yandex.ru/v1/"
        api_key = API_MAPS
        search_params = {
            "apikey": api_key,
            "text": obj,
            "lang": "ru_RU",
            "ll": address_ll,
            "type": "biz"
        }
        response = requests.get(search_api_server, params=search_params)
        print(response.json())
        json_response = response.json()
        json_response['features'] = json_response['features'][:6]
        return '\n\n'.join(
            [VK_NUMBERS_LIST[i] + json_response["features"][i]['properties'][
                'name'] + ' ' + json_response["features"][i]['properties'][
                 'description'] for i in
             range(len(json_response["features"]))]), len(
            json_response["features"])

    def choose_number(self, geo, object):
        objects, count = self.get_list_of_objects(geo, object)
        if objects:
            keyboard = create_keyboard.create_keyboard(buttons=NUMBERS[:count],
                                                   inline=False)
            self.vk.messages.send(user_id=self.user_id,
                              message=f'Выберите объект\n\n' + objects,
                              random_id=random.randint(0, 2 ** 64),
                              keyboard=keyboard)
        else:
            self.not_found()

    def set_centr(self, coor_1, coor_2):
        x1, y1 = map(float, coor_1.split(','))
        x2, y2 = map(float, coor_2.split(','))
        return [str((x1 + x2) / 2), str((y1 + y2) / 2)]

    def get_map(self, address_ll, obj, i):
        search_api_server = "https://search-maps.yandex.ru/v1/"
        api_key = API_MAPS
        search_params = {
            "apikey": api_key,
            "text": obj,
            "lang": "ru_RU",
            "ll": address_ll,
            "type": "biz"
        }
        if i - 1 not in range(6):
            i = 1
        response = requests.get(search_api_server, params=search_params)
        json_response = response.json()
        obj_ll = ','.join(list(
            map(str,
                json_response['features'][i - 1]['geometry']['coordinates'])))
        centr = ','.join(self.set_centr(address_ll, obj_ll))
        map_request = f"http://static-maps.yandex.ru/1.x/"
        params = {
            'll': centr,
            'l': 'map',
            'pt': '~'.join([address_ll + ',ya_ru', obj_ll + ',comma'])
        }
        response = requests.get(map_request, params=params)
        return response.content, \
               json_response["features"][i - 1]['properties'][
                   'name'] + ' ' + \
               json_response["features"][i - 1]['properties'][
                   'description']

    def send_map(self, geo, obj, num):
        map = self.get_map(geo, obj, num)
        map_file = "static/img/map.jpg"
        with open(map_file, "wb") as file:
            file.write(map[0])
        url = self.vk.photos.getMessagesUploadServer()

        response = requests.post(url=url['upload_url'],
                                 files={'photo': open(map_file,
                                                      'rb')}).json()

        photo_info = self.vk.photos.saveMessagesPhoto(
            photo=response['photo'],
            server=response['server'],
            hash=response['hash'])[0]
        photo = f'photo{photo_info["owner_id"]}_{photo_info["id"]}'
        self.client.hdel(self.user_id, 'state')
        keyboard = create_keyboard.create_keyboard(
            buttons=COMMAND_LIST,
            inline=False, geo=True)
        self.vk.messages.send(user_id=self.user_id,
                              message=map[1],
                              random_id=random.randint(0,
                                                       2 ** 64),
                              attachment=photo,
                              keyboard=keyboard)

    def not_found(self):
        self.client.hdel(self.user_id, 'state')
        keyboard = create_keyboard.create_keyboard(
            buttons=COMMAND_LIST,
            inline=False, geo=True)
        self.vk.messages.send(user_id=self.user_id,
                              message=f'Поблизости ничего не найдено',
                              random_id=random.randint(0, 2 ** 64),
                              keyboard=keyboard)
