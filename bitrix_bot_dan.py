import random
from bitrix24 import *
import redis
import vk_api
import logging
import requests
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from config import *

FIELD_DICT = {'phone_field': 'UF_CRM_1588189272167',
              'email_field': 'UF_CRM_1588189283184',
              'vk_field': 'UF_CRM_1588188854996'}
PRODUCT_DICT = {'вконтакте': {"PRODUCT_ID": 9, "PRICE": 4000},
                'telegram': {"PRODUCT_ID": 7, "PRICE": 5000.00},
                'other.platform': {"PRODUCT_ID": 15, "PRICE": 4500.00},
                'чат-бот': {"PRODUCT_ID": 1, "PRICE": 1000},
                'бот-автоответчик': {"PRODUCT_ID": 3, "PRICE": 500},
                "бот-игра": {"PRODUCT_ID": 5, "PRICE": 2000},
                'other.bot': {"PRODUCT_ID": 17, "PRICE": 1200},
                'сообщество': {"PRODUCT_ID": 13, "PRICE": 300},
                'страница': {"PRODUCT_ID": 11, "PRICE": 100}}
logging.basicConfig(level=logging.INFO)


def create_keyboard(buttons=[], inline=False, one_time=False, d=3, ask=True):
    keyboard = VkKeyboard(one_time=one_time, inline=inline)
    line = False
    for i in range(len(buttons) // d):
        for j in range(d):
            keyboard.add_button(buttons[i * d + j][0],
                                color=buttons[i * d + j][1])
        if ask:
            keyboard.add_line()
        else:
            if i * d + j != len(buttons) - 1:
                keyboard.add_line()
        line = True
    for i in range(len(buttons) % d):
        keyboard.add_button(buttons[- i - 1][0],
                            color=buttons[- i - 1][1])
        line = False
    if ask:
        if not line and len(buttons) != 0:
            keyboard.add_line()
        keyboard.add_button('Задать вопрос', VkKeyboardColor.POSITIVE)
    return keyboard.get_keyboard()


class BitrixBot():
    def __init__(self, vk, client, id):
        self.vk = vk
        self.btx = Bitrix24(
            f'https://{DOMAIN}.bitrix24.ru/rest/1/{TOKEN_BITRIX}')
        self.client = client
        self.user_id = id
        self.FUNCTION_DICT = {'start': self.start,
                              'platform': self.platform,
                              'category': self.category,
                              'char_1': self.char_1, 'accept': self.accept,
                              'description': self.description,
                              'contact': self.contact, 'manager': self.manager}

    def analyse_type(self, message):
        if message['attachments']:
            if 'sticker' in message['attachments'][0]:
                self.vk.messages.send(user_id=self.user_id,
                                      sticker_id=15131,
                                      random_id=random.randint(0, 2 ** 64))
        else:
            text = message['text'].lower().strip()
            self.analyse_text(text)

    def analyse_text(self, text):
        if text == 'начать':
            self.client.hset(self.user_id, "now", 'start')
            keyboard = create_keyboard(
                buttons=[['Хочу бота', VkKeyboardColor.POSITIVE]])

            response = self.vk.users.get(user_id=self.user_id)[0]
            print(response)
            id = self.btx.callMethod("crm.contact.add",
                                     fields={'TYPE_ID': 'CLIENT',
                                             'NAME': response['first_name'],
                                             'LAST_NAME': response[
                                                 'last_name'],
                                             "IM": [{"VALUE": 'id' + str(
                                                 response['id']),
                                                     'VALUE_TYPE': 'VK'}]})
            self.client.hset(self.user_id, 'contact_id', id)
            self.vk.messages.send(user_id=self.user_id,
                                  message=f'Вас приветствует служба покупки ботов от проекта 2DYeS&#128104;&#8205;&#128187;',
                                  random_id=random.randint(0, 2 ** 64))
            self.vk.messages.send(user_id=self.user_id,
                                  message=f'Следуйте инструкциям на клавиатуре&#9000;',
                                  random_id=random.randint(0, 2 ** 64),
                                  keyboard=keyboard)

        elif text == 'задать вопрос':
            self.ask()
        else:
            try:
                state = self.client.hget(self.user_id, "now").decode('utf-8')
            except Exception:
                state = 'start'
                self.client.hset(self.user_id, "now", 'start')
            logging.info(state)
            self.FUNCTION_DICT[state](text)

    def ask(self):
        pass

    def start(self, text):
        if text == 'хочу бота':
            contact_id = self.client.hget(self.user_id, 'contact_id').decode(
                'utf-8')

            id = self.btx.callMethod("crm.deal.add",
                                     fields={'CONTACT_ID': contact_id})
            self.client.hset(self.user_id, 'id', id)
            self.client.hset(self.user_id, 'now', "platform")
            keyboard = create_keyboard(
                buttons=[['Вконтакте', VkKeyboardColor.DEFAULT],
                         ['Telegram', VkKeyboardColor.DEFAULT]], d=2)
            self.vk.messages.send(user_id=self.user_id,
                                  message=f'Выберите платформу бота (или укажите свою)&#128221;',
                                  random_id=random.randint(0, 2 ** 64),
                                  keyboard=keyboard)

    def platform(self, text):
        if text not in ['вконтакте', 'telegram']:
            text = 'other.platform'
        self.client.hset(self.user_id, 'products', text)
        id = self.client.hget(self.user_id, 'id').decode(
            'utf-8')
        self.set_products(id)
        self.client.hset(self.user_id, 'now', "category")
        keyboard = create_keyboard(
            buttons=[['Чат-бот', VkKeyboardColor.DEFAULT],
                     ['Бот-игра', VkKeyboardColor.DEFAULT],
                     ['Бот-автоответчик', VkKeyboardColor.DEFAULT]], d=2)
        self.vk.messages.send(user_id=self.user_id,
                              message=f'Выберите категорию бота (или укажите свою)&#128221;',
                              random_id=random.randint(0, 2 ** 64),
                              keyboard=keyboard)

    def category(self, text):
        if text not in []:
            text = 'other.bot'
        self.client.hset(self.user_id, 'products', self.client.hget(self.user_id, 'products').decode('utf-8') + '_' + text)
        id = self.client.hget(self.user_id, 'id').decode('utf-8')
        self.set_products(id)
        self.client.hset(self.user_id, "now", 'char_1')
        keyboard = create_keyboard()
        self.vk.messages.send(user_id=self.user_id,
                              message='Пройдите опрос&#128196;',
                              random_id=random.randint(0, 2 ** 64),
                              keyboard=keyboard)
        keyboard = create_keyboard(
            buttons=[['Сообщество', VkKeyboardColor.PRIMARY],
                     ['Страница', VkKeyboardColor.PRIMARY]], d=2,
            ask=False, inline=True)
        self.vk.messages.send(user_id=self.user_id,
                              message=f'К чему подключено?',
                              random_id=random.randint(0, 2 ** 64),
                              keyboard=keyboard)

    def char_1(self, text):
        if text in ['сообщество', 'страница']:
            self.client.hset(self.user_id, "char_1", text)
            self.client.hset(self.user_id, "now", "accept")
            self.client.hset(self.user_id, 'products',
                             self.client.hget(self.user_id, 'products').decode(
                                 'utf-8') + '_' + text)
            id = self.client.hget(self.user_id, 'id').decode('utf-8')
            self.set_products(id)
            self.btx.callMethod("crm.deal.update", ID=id,
                                fields={'STAGE_ID': 'PREPARATION'})
            cost = int(self.btx.callMethod('crm.deal.get', ID=id)['OPPORTUNITY'].split('.')[0])
            keyboard = create_keyboard(
                buttons=[['Я согласен с условиями', VkKeyboardColor.POSITIVE],
                         ['Отменить заказ', VkKeyboardColor.NEGATIVE]], d=1,
                ask=False)
            self.vk.messages.send(user_id=self.user_id,
                                  message=f'Предварительная стоимость составляет {cost}\nПредоплата {cost * 0.3}\nВы согласны с условиями?',
                                  random_id=random.randint(0, 2 ** 64),
                                  keyboard=keyboard)

    def accept(self, text):
        if text.startswith('я согласен'):
            self.client.hset(self.user_id, "now", "description")
            id = self.client.hget(self.user_id, 'id').decode('utf-8')
            self.btx.callMethod("crm.deal.update", ID=id,
                                fields={'STAGE_ID': 'PREPAYMENT_INVOICE'})
            keyboard = create_keyboard(
                buttons=[['Продолжить', VkKeyboardColor.PRIMARY]])
            self.vk.messages.send(user_id=self.user_id,
                                  message='Кратко опишите вашу идею и нажмите "Продолжить"',
                                  random_id=random.randint(0, 2 ** 64),
                                  keyboard=keyboard)
        elif text.startswith('отменить'):
            self.client.hset(self.user_id, "now", 'start')
            id = self.client.hget(self.user_id, 'id').decode('utf-8')
            self.btx.callMethod("crm.deal.update", ID=id,
                                fields={'STAGE_ID': 'LOSE'})
            keyboard = create_keyboard(
                buttons=[['Хочу бота', VkKeyboardColor.POSITIVE]])
            self.vk.messages.send(user_id=self.user_id,
                                  message=f'Вас приветствует служба покупки ботов от проекта 2DYeS&#128104;&#8205;&#128187;',
                                  random_id=random.randint(0, 2 ** 64))
            self.vk.messages.send(user_id=self.user_id,
                                  message=f'Следуйте инструкциям на клавиатуре&#9000;',
                                  random_id=random.randint(0, 2 ** 64),
                                  keyboard=keyboard)

    def description(self, text):
        if text == "продолжить":
            try:
                comment = self.client.hget(self.user_id, 'comment').decode(
                    'utf-8')
                self.client.hdel(self.user_id, 'comment')
                id = self.client.hget(self.user_id, 'id').decode('utf-8')
                self.btx.callMethod('crm.deal.update', ID=id,
                                    fields={'COMMENTS': comment})
            except:
                pass
            self.client.hset(self.user_id, "now", 'contact')
            keyboard = create_keyboard(
                buttons=[['Вконтакте', VkKeyboardColor.DEFAULT],
                         ['Email', VkKeyboardColor.DEFAULT],
                         ['Viber', VkKeyboardColor.DEFAULT],
                         ['Telegram', VkKeyboardColor.DEFAULT],
                         ['Звонок на мобильный', VkKeyboardColor.DEFAULT]],
                d=2)
            self.vk.messages.send(user_id=self.user_id,
                                  message=f'Как нам с вами связаться?',
                                  random_id=random.randint(0, 2 ** 64),
                                  keyboard=keyboard)
        else:
            comment = ''
            try:
                comment += self.client.hget(self.user_id, 'comment').decode(
                    'utf-8')
            except Exception:
                pass
            comment += '\n' + text
            self.client.hset(self.user_id, 'comment', comment)

    def contact(self, text):
        if text.startswith('вк'):
            self.client.hset(self.user_id, "contact", "VK")
            self.client.hset(self.user_id, "now", 'manager')
            return self.manager(text)
        elif text == 'email':
            self.client.hset(self.user_id, "contact", "EMAIL")
            self.client.hset(self.user_id, "now", 'manager')
            keyboard = create_keyboard(
                buttons=[])
            self.vk.messages.send(user_id=self.user_id,
                                  message='Введите ваш адрес email',
                                  random_id=random.randint(0, 2 ** 64),
                                  keyboard=keyboard)
        elif text.startswith('звонок') or text.startswith(
                'viber') or text.startswith('telegram'):
            self.client.hset(self.user_id, "contact", "PHONE-" + text.upper())
            self.client.hset(self.user_id, "now", 'manager')
            keyboard = create_keyboard(
                buttons=[])
            self.vk.messages.send(user_id=self.user_id,
                                  message='Введите ваш номер телефона',
                                  random_id=random.randint(0, 2 ** 64),
                                  keyboard=keyboard)

    def manager(self, text):
        contact = \
            self.client.hget(self.user_id, "contact").decode('utf-8')
        id = self.client.hget(self.user_id, 'id').decode('utf-8')
        self.btx.callMethod("crm.deal.update", ID=id,
                            fields={'STAGE_ID': 'EXECUTING'})
        if contact.startswith('VK'):
            pass
        elif contact.startswith('EMAIL'):
            contact_id = self.client.hget(self.user_id, 'contact_id').decode(
                'utf-8')
            self.btx.callMethod('crm.contact.update', ID=contact_id,
                                fields={'EMAIL': [{"VALUE": text}]})
        elif contact.startswith('PHONE'):
            print('ok')
            contact_id = self.client.hget(self.user_id, 'contact_id').decode(
                'utf-8')
            contact = contact.split('-')[1]
            response = self.vk.users.get(user_id=self.user_id)[0]
            if contact in ['VIBER', 'TELEGRAM']:
                self.btx.callMethod('crm.contact.update', ID=contact_id,
                                    fields={"IM": [{"VALUE": 'id' + str(
                                        response['id']), 'VALUE_TYPE': 'VK'},
                                                   {"VALUE": text,
                                                    'VALUE_TYPE': contact}]})
            self.btx.callMethod('crm.contact.update', ID=contact_id,
                                fields={'PHONE': [{"VALUE": text}]})
        self.client.hset(self.user_id, "now", 'start')
        keyboard = create_keyboard(
            buttons=[['Хочу бота', VkKeyboardColor.POSITIVE]])
        self.vk.messages.send(user_id=self.user_id,
                              message=f'В течении следующего часа с вами свяжется менеджер для оговорения стоимости и сроков сдачи.\nОжидайте...',
                              random_id=random.randint(0, 2 ** 64),
                              keyboard=keyboard)

    def set_products(self, id):
        search = f'https://{DOMAIN}.bitrix24.ru/rest/1/{TOKEN_BITRIX}/crm.deal.productrows.set/?id={id}'
        products = self.client.hget(self.user_id, 'products').decode('utf-8').split('_')
        for i in range(len(products)):
            search += f'&rows[{i}][PRODUCT_ID]={PRODUCT_DICT[products[i]]["PRODUCT_ID"]}&rows[{i}][PRICE]={PRODUCT_DICT[products[i]]["PRICE"]}'
        requests.get(search)




def info_about_user(id, state):
    pass


def main():
    print('----------------------------------------------------------')
    vk_session = vk_api.VkApi(
        token=TOKEN)
    longpoll = VkBotLongPoll(vk_session, GROUP_ID)
    vk = vk_session.get_api()
    client = redis.Redis()
    logging.info('Бот запущен...')

    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            bitrix_bot = BitrixBot(vk, client, event.obj.message['from_id'])
            bitrix_bot.analyse_type(event.obj.message)


if __name__ == '__main__':
    main()
