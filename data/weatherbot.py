import calendar
import random
from datetime import datetime
from config import *
import requests
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from .constants import *
from . import create_keyboard


class WeatherBot:
    def __init__(self, vk, user_id, client, command):
        self.vk = vk
        self.user_id = user_id
        self.client = client
        self.command = command
        self.WEATHER_FUNC = {'погода сейчас': self.weather_now,
                             'прогноз на сегодня': self.weather_today,
                             'прогноз на завтра': self.weather_tomorrow, 'прогноз на неделю': self.weather_week}

    def analyse_command(self):
        geo = self.client.hget(self.user_id, 'geo')

        if geo:
            geo = geo.decode('utf-8')
            time = self.client.hget(self.user_id, 'create_time').decode(
                'utf-8').split('.')[0]
            time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
            delta_time = str(
                datetime.now() - time).split()
            if delta_time[0].split(':')[0] == '0':
                command = self.command.split()
                if len(command) == 1:
                    self.choose_weather()
                else:
                    self.WEATHER_FUNC[' '.join(command[1:])](geo)
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

    def choose_weather(self):
        keyboard = create_keyboard.create_keyboard(buttons=
                                                   COMMAND_DICT['!погода'][
                                                       'категории'],
                                                   inline=False, d=2)

        self.vk.messages.send(user_id=self.user_id,
                              message=f'Выберите прогноз',
                              random_id=random.randint(0, 2 ** 64),
                              keyboard=keyboard)

    def weather_now(self, geo):
        params = {'lat': geo.split(',')[1],
                  'lon': geo.split(',')[0],
                  'lang': 'ru_RU',
                  'limit': 7,
                  'extra': 'true',
                  'hours': 'true'
                  }
        response = requests.get('https://api.weather.yandex.ru/v1/forecast?',
                                params=params, headers={
                'X-Yandex-API-Key': API_WEATHER}).json()

        self.client.hdel(self.user_id, 'state')
        keyboard = create_keyboard.create_keyboard(
            buttons=COMMAND_LIST,
            inline=False, geo=True)
        self.vk.messages.send(user_id=self.user_id,
                              message=self.make_weather(response['fact']),
                              random_id=random.randint(0,
                                                       2 ** 64),
                              keyboard=keyboard)

    def weather_today(self, geo):
        params = {'lat': geo.split(',')[1],
                  'lon': geo.split(',')[0],
                  'lang': 'ru_RU',
                  'limit': 7,
                  'extra': 'true',
                  'hours': 'true'
                  }
        response = requests.get('https://api.weather.yandex.ru/v1/forecast?',
                                params=params, headers={
                'X-Yandex-API-Key': API_WEATHER}).json()

        self.client.hdel(self.user_id, 'state')
        keyboard = create_keyboard.create_keyboard(
            buttons=COMMAND_LIST,
            inline=False, geo=True)
        self.vk.messages.send(user_id=self.user_id,
                              message=self.make_forecast(response['forecasts'][:1]),
                              random_id=random.randint(0,
                                                       2 ** 64),
                              keyboard=keyboard)

    def weather_tomorrow(self, geo):
        params = {'lat': geo.split(',')[1],
                  'lon': geo.split(',')[0],
                  'lang': 'ru_RU',
                  'limit': 7,
                  'extra': 'true',
                  'hours': 'true'
                  }
        response = requests.get('https://api.weather.yandex.ru/v1/forecast?',
                                params=params, headers={
                'X-Yandex-API-Key': API_WEATHER}).json()

        self.client.hdel(self.user_id, 'state')
        keyboard = create_keyboard.create_keyboard(
            buttons=COMMAND_LIST,
            inline=False, geo=True)
        self.vk.messages.send(user_id=self.user_id,
                              message=self.make_forecast(
                                  response['forecasts'][1:2]),
                              random_id=random.randint(0,
                                                       2 ** 64),
                              keyboard=keyboard)

    def weather_week(self, geo):
        params = {'lat': geo.split(',')[1],
                  'lon': geo.split(',')[0],
                  'lang': 'ru_RU',
                  'limit': 7,
                  'extra': 'true',
                  'hours': 'true'
                  }
        response = requests.get('https://api.weather.yandex.ru/v1/forecast?',
                                params=params, headers={
                'X-Yandex-API-Key': API_WEATHER}).json()

        self.client.hdel(self.user_id, 'state')
        keyboard = create_keyboard.create_keyboard(
            buttons=COMMAND_LIST,
            inline=False, geo=True)
        self.vk.messages.send(user_id=self.user_id,
                              message=self.make_forecast(
                                  response['forecasts']),
                              random_id=random.randint(0,
                                                       2 ** 64),
                              keyboard=keyboard)

    def make_weather(self, weather):
        condition = f'''{"".join(WEATHER_CONDITION[weather["condition"]][::-1])}\n'''
        temp = f'''&#127777;Температура воздуха: {weather["temp"]}\u00B0C
Ощущается как: {weather["feels_like"]}\u00B0C
&#128167;Температура воды: {weather["temp_water"]}\u00B0C\n'''
        wind = f'''&#128168;Ветер: {WIND[weather["wind_dir"]]} {weather["wind_speed"]} м/с\n'''
        pressure = f'''&#127760;Атм. давление: {weather["pressure_mm"]} мм рт. ст.\n'''
        humidity = f'''&#128166;Влажность воздуха: {weather["humidity"]}%'''
        return condition + temp + wind + pressure + humidity

    def get_day_week(self, date):
        date = calendar.weekday(int(date.split('-')[0]),
                                int(date.split('-')[1]),
                                int(date.split('-')[2]))
        return WEEK[str(date)]

    def make_forecast(self, weather):
        weather_list = []
        for elem in weather:
            head = self.get_day_week(elem['date']).title() + ' ' + '.'.join(elem['date'].split('-')[::-1]) + '\n'
            t_max = f"&#128200;Температура днем: {elem['parts']['day']['temp_max']}\u00B0C\n"
            t_min = f"&#128201;Температура ночью: {elem['parts']['night']['temp_min']}\u00B0C\n"
            main_weather = self.make_weather(elem['parts']['day_short'])
            weather_list.append(head + t_max + t_min + main_weather)
        return '\n\n'.join(weather_list)