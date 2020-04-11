from vk_api.keyboard import VkKeyboardColor

DATETIME = {'01': "января", '02': "февраля", '03': "марта", '04': "апреля",
            '05': "мая", '06': "июня", '07': "июля", '08': "августа",
            '09': "сентября", '10': "октября", '11': "ноября", '12': "декабря"}
WEEK = {'0': 'понедельник', '1': 'вторник', '2': 'среда', '3': 'четверг',
        '4': 'пятница', '5': 'суббота', '6': 'воскресенье', }
URL = "https://translate.yandex.net/api/v1.5/tr.json/translate"
KEY_TRANSLATE = 'trnsl.1.1.20200326T112517Z.b892e6716bd0b2a8.fd91d2d249350b7b7642829f4d1a70a616d9fb3e'
COMMAND_DICT = {
    '!гео': {
        'помощь': 'Сервис предлагает поиск компании по выбранной категории и отображает ее на карте.\n1) Выберите одну из предложенных категорий или напишите свою (имениительный патеж, единственное число, регистр неважен).\n2) Далее выберите компанию, нажав на соответствующую кнопку на клавиатуре.\nНе теряйтесь&#128517;',
        'категории': [['Продукты', VkKeyboardColor.PRIMARY],
                      ['Метро', VkKeyboardColor.PRIMARY],
                      ['Аптека', VkKeyboardColor.PRIMARY]]},
    '!погода': {
        'помощь': "Сервис предлагает прогнозы погоды различной длительности, вам остается лишь выбрать&#128540;",
        'категории': [['Погода сейчас', VkKeyboardColor.PRIMARY],
                      ['Прогноз на сегодня', VkKeyboardColor.PRIMARY],
                      ['Прогноз на завтра', VkKeyboardColor.PRIMARY],
                      ['Прогноз на неделю', VkKeyboardColor.PRIMARY]]},
    '!новости': {
        'помощь': "Сервис предлагает подборку новостей на разные темы, вам остается лишь выбрать&#128540;",
        'категории': [['Здоровье', VkKeyboardColor.PRIMARY],
                      ['Смерть', VkKeyboardColor.PRIMARY],
                      ['ДТП', VkKeyboardColor.PRIMARY],
                      ['Преступления', VkKeyboardColor.PRIMARY],
                      ['Политика', VkKeyboardColor.PRIMARY],
                      ['Бизнес', VkKeyboardColor.PRIMARY],
                      ['Плохие новости', VkKeyboardColor.PRIMARY],
                      ['Хорошие новости', VkKeyboardColor.PRIMARY],
                      ['СOVID-19', VkKeyboardColor.PRIMARY]]}, }
COMMAND_LIST = [
    ['!Гео', VkKeyboardColor.DEFAULT],
    ['!Погода', VkKeyboardColor.DEFAULT],
    ['!Новости', VkKeyboardColor.DEFAULT],
    ['!Помощь', VkKeyboardColor.POSITIVE]
]
NUMBERS = [['&#49;&#8419;', VkKeyboardColor.DEFAULT],
           ['&#50;&#8419;', VkKeyboardColor.DEFAULT],
           ['&#51;&#8419;', VkKeyboardColor.DEFAULT],
           ['&#52;&#8419;', VkKeyboardColor.DEFAULT],
           ['&#53;&#8419;', VkKeyboardColor.DEFAULT],
           ['&#54;&#8419;', VkKeyboardColor.DEFAULT],
           ['7', VkKeyboardColor.PRIMARY], ['8', VkKeyboardColor.PRIMARY],
           ['9', VkKeyboardColor.PRIMARY], ['10', VkKeyboardColor.PRIMARY]]
VK_NUMBERS_LIST = ['&#49;&#8419;', '&#50;&#8419;', '&#51;&#8419;',
                   '&#52;&#8419;',
                   '&#53;&#8419;', '&#54;&#8419;']

VK_NUMBERS_DICT = {'&#49;&#8419;': 1, '&#50;&#8419;': 2, '&#51;&#8419;': 3,
                   '&#52;&#8419;': 4,
                   '&#53;&#8419;': 5, '&#54;&#8419;': 6}
HELP_LIST = [['Гео', VkKeyboardColor.POSITIVE],
             ['Погода', VkKeyboardColor.POSITIVE],
             ['Новости', VkKeyboardColor.POSITIVE]]
WEATHER_CONDITION = {'clear': ['ясно'.title(), '&#9728;'],
                     'partly-cloudy': ['малооблачно'.title(), '&#127780;'],
                     'cloudy': ['облачно с прояснениями'.title(), '&#9925;'],
                     'overcast': ['пасмурно'.title(), '&#9729;'],
                     'partly-cloudy-and-light-rain': [
                         'небольшой дождь'.title(),
                         '&#127782;'],
                     'partly-cloudy-and-rain': ['дождь'.title(), '&#127783;'],
                     'overcast-and-rain': ['сильный дождь'.title(), '&#9748;'],
                     'overcast-thunderstorms-with-rain': [
                         'сильный дождь, гроза'.title(), '&#9928;'],
                     'cloudy-and-light-rain': ['небольшой дождь'.title(),
                                               '&#127782;'],
                     'overcast-and-light-rain': ['небольшой дождь'.title(),
                                                 '&#127782;'],
                     'cloudy-and-rain': ['дождь'.title(), '&#127783;'],
                     'overcast-and-wet-snow': ['дождь со снегом'.title(),
                                               '&#9928;'],
                     'partly-cloudy-and-light-snow': ['небольшой снег'.title(),
                                                      '&#10052;'],
                     'partly-cloudy-and-snow': ['снег'.title(), '&#127784;'],
                     'overcast-and-snow': ['снегопад'.title(), '&#127784;'],
                     'cloudy-and-light-snow': ['небольшой снег'.title(),
                                               '&#10052;'],
                     'overcast-and-light-snow': ['небольшой снег'.title(),
                                                 '&#10052;'],
                     'cloudy-and-snow': ['снег'.title(), '&#127784;']}
WIND = {'nw': 'северо-западный', 'n': 'северный', 'ne': 'северо-восточный',
        'e': 'восточный', 'se': 'юго-восточный', 's': 'южный',
        'sw': 'юго-западный', 'w': 'западный', 'с': 'штиль'}

NEWS = {'здоровье': ['HEALTH'.lower(),
                     'Федеральное медико-биологическое агентство'.lower(),
                     'ВОЗ'.lower(), 'Минздрав РФ'.lower()],
        'смерть': ['DEATH'.lower()],
        'дтп': ['ROAD-ACCIDENT'.lower(), 'ГИБДД'.lower()],
        'преступления': ['CRIME'.lower()],
        'политика': ["POLITIC".lower(), 'ЕС'.lower()],
        'бизнес': ['BUSINESS'.lower(), 'FINANCE'.lower()],
        'плохие новости': ['Negative text'.lower(), 'NEGATIVITY_WEAK'.lower()],
        'сovid-19': ['COVID'.lower()],
        'хорошие новости': ['Positive text'.lower()]}
