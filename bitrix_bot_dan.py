import random
from bitrix24 import *
import redis
import vk_api
import logging

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from config import *

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
                              'organisation': self.organisation,
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
            try:
                id = self.client.hget(self.user_id, 'id').decode('utf-8')
                self.btx.callMethod('crm.lead.delete', ID=id)
            except Exception as e:
                print(e)
            response = self.vk.users.get(user_id=self.user_id)[0]
            print(response)
            id = self.btx.callMethod("crm.lead.add",
                                     fields={'STATUS_ID': 'NEW',
                                             'NAME': response['first_name'],
                                             'LAST_NAME': response[
                                                 'last_name']},
                                     params={"REGISTER_SONET_EVENT": "Y"})
            self.client.hset(self.user_id, 'id', id)
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
            id = self.client.hget(self.user_id, 'id').decode('utf-8')
            self.btx.callMethod("crm.lead.update", ID=id,
                                fields={'STATUS_ID': 'IN_PROCESS'})
            self.client.hset(self.user_id, 'now', "organisation")
            keyboard = create_keyboard(
                buttons=[['Физ.лицо', VkKeyboardColor.PRIMARY]])
            self.vk.messages.send(user_id=self.user_id,
                                  message=f'Напишите название организации',
                                  random_id=random.randint(0, 2 ** 64),
                                  keyboard=keyboard)

    def organisation(self, text):
        id = self.client.hget(self.user_id, 'id').decode('utf-8')
        self.btx.callMethod("crm.lead.update", ID=id,
                            fields={'TITLE': text.title()})
        self.client.hset(self.user_id, 'now', "platform")
        keyboard = create_keyboard(
            buttons=[['Вконтакте', VkKeyboardColor.DEFAULT],
                     ['Телеграмм', VkKeyboardColor.DEFAULT]], d=2)
        self.vk.messages.send(user_id=self.user_id,
                              message=f'Выберите платформу бота (или укажите свою)&#128221;',
                              random_id=random.randint(0, 2 ** 64),
                              keyboard=keyboard)

    def platform(self, text):
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
            id = self.client.hget(self.user_id, 'id').decode('utf-8')
            self.btx.callMethod("crm.lead.update", ID=id,
                                fields={'STATUS_ID': 'PROCESSED'})
            result = self.btx.callMethod("crm.lead.get", ID=id)
            print(result)
            self.btx.callMethod('crm.deal.add', fields=result)
            keyboard = create_keyboard(
                buttons=[['Я согласен с условиями', VkKeyboardColor.POSITIVE],
                         ['Отменить заказ', VkKeyboardColor.NEGATIVE]], d=1,
                ask=False)
            self.vk.messages.send(user_id=self.user_id,
                                  message=f'Предварительная стоимость составляет ...\nПредоплата ...%\nВы согласны с условиями?',
                                  random_id=random.randint(0, 2 ** 64),
                                  keyboard=keyboard)

    def accept(self, text):
        if text.startswith('я согласен'):
            self.client.hset(self.user_id, "now", "description")
            id = self.client.hget(self.user_id, 'id').decode('utf-8')
            self.btx.callMethod("crm.lead.update", ID=id,
                                fields={'STATUS_ID': 'CONVERTED'})
            keyboard = create_keyboard(
                buttons=[['Продолжить', VkKeyboardColor.PRIMARY]])
            self.vk.messages.send(user_id=self.user_id,
                                  message='Кратко опишите вашу идею и нажмите "Продолжить"',
                                  random_id=random.randint(0, 2 ** 64),
                                  keyboard=keyboard)
        elif text.startswith('отменить'):
            self.client.hset(self.user_id, "now", 'start')
            id = self.client.hget(self.user_id, 'id').decode('utf-8')
            self.btx.callMethod("crm.lead.update", ID=id,
                                fields={'STATUS_ID': 'JUNK'})
            try:
                id = self.client.hget(self.user_id, 'id').decode('utf-8')
                self.btx.callMethod('crm.lead.delete', ID=id)
            except Exception as e:
                print(e)
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
            self.client.hset(self.user_id, "now", 'contact')
            keyboard = create_keyboard(
                buttons=[['Вконтакте', VkKeyboardColor.DEFAULT],
                         ['Email', VkKeyboardColor.DEFAULT],
                         ['Номер телефона', VkKeyboardColor.DEFAULT]], d=2)
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
        elif text.startswith('номер'):
            self.client.hset(self.user_id, "contact", "PHONE")
            self.client.hset(self.user_id, "now", 'manager')
            keyboard = create_keyboard(
                buttons=[])
            self.vk.messages.send(user_id=self.user_id,
                                  message='Введите ваш номер телефона',
                                  random_id=random.randint(0, 2 ** 64),
                                  keyboard=keyboard)
        else:
            pass

    def manager(self, text):
        contact = \
            self.client.hget(self.user_id, "contact").decode('utf-8')
        if contact == 'VK':
            print(self.btx.callMethod("crm.lead.add", fields={
                "TITLE": f"Заказ {self.vk.users.get(user_id=self.user_id)[0]['first_name']}{self.vk.users.get(user_id=self.user_id)[0]['last_name']}.Категория:{self.client.hget(self.user_id, 'category').decode('utf-8')}",
                "NAME": f"{self.vk.users.get(user_id=self.user_id)[0]['first_name']}",
                "LAST_NAME": f"{self.vk.users.get(user_id=self.user_id)[0]['last_name']}",
                "STATUS_ID": "NEW",
                "OPENED": "Y",
                "ASSIGNED_BY_ID": 1,
                "COMMENTS": f"Категория бота: {self.client.hget(self.user_id, 'category').decode('utf-8')}, для {self.client.hget(self.user_id, 'char_1').decode('utf-8')}\n Информация от заказчика:{self.client.hget(self.user_id, 'comment').decode('utf-8')}.\n Удобно связаться через {self.client.hget(self.user_id, 'contact').decode('utf-8')}"},
                                      params={"REGISTER_SONET_EVENT": "Y"}))
        elif contact == 'EMAIL':
            self.btx.callMethod("crm.lead.add", fields={
                "TITLE": f"Заказ {self.vk.users.get(user_id=self.user_id)[0]['first_name']}{self.vk.users.get(user_id=self.user_id)[0]['last_name']}.Категория:{self.client.hget(self.user_id, 'category').decode('utf-8')}",
                "NAME": f"{self.vk.users.get(user_id=self.user_id)[0]['first_name']}",
                "LAST_NAME": f"{self.vk.users.get(user_id=self.user_id)[0]['last_name']}",
                "STATUS_ID": "NEW",
                "OPENED": "Y",
                "ASSIGNED_BY_ID": 1,
                "COMMENTS": f"Категория бота: {self.client.hget(self.user_id, 'category').decode('utf-8')}, для {self.client.hget(self.user_id, 'char_1').decode('utf-8')}\n Информация от заказчика:{self.client.hget(self.user_id, 'comment').decode('utf-8')}.\n Удобно связаться через {self.client.hget(self.user_id, 'contact').decode('utf-8')}"},
                                params={"REGISTER_SONET_EVENT": "Y"})
        elif contact == 'PHONE':
            self.btx.callMethod("crm.lead.add", fields={
                "TITLE": f"Заказ {self.vk.users.get(user_id=self.user_id)[0]['first_name']}{self.vk.users.get(user_id=self.user_id)[0]['last_name']}.Категория:{self.client.hget(self.user_id, 'category').decode('utf-8')}",
                "NAME": f"{self.vk.users.get(user_id=self.user_id)[0]['first_name']}",
                "LAST_NAME": f"{self.vk.users.get(user_id=self.user_id)[0]['last_name']}",
                "STATUS_ID": "NEW",
                "OPENED": "Y",
                "ASSIGNED_BY_ID": 1,
                "COMMENTS": f"Категория бота: {self.client.hget(self.user_id, 'category').decode('utf-8')}, для {self.client.hget(self.user_id, 'char_1').decode('utf-8')}\n Информация от заказчика:{self.client.hget(self.user_id, 'comment').decode('utf-8')}.\n Удобно связаться через {self.client.hget(self.user_id, 'contact').decode('utf-8')}"},
                                params={"REGISTER_SONET_EVENT": "Y"})
        self.client.hset(self.user_id, "now", 'start')
        keyboard = create_keyboard(
            buttons=[['Хочу бота', VkKeyboardColor.POSITIVE]])
        self.vk.messages.send(user_id=self.user_id,
                              message=f'В течении следующего часа с вами свяжется менеджер для оговорения стоимости и сроков сдачи.\nОжидайте...',
                              random_id=random.randint(0, 2 ** 64),
                              keyboard=keyboard)


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
