import random
from bitrix24 import *
import redis
import vk_api
import logging

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from config import TOKEN, GROUP_ID

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
    def __init__(self, vk, client, id, tok):
        self.vk = vk
        self.btx = Bitrix24(f'https://b24-llmh5i.bitrix24.ru/rest/1/{tok}')
        self.client = client
        self.user_id = id
        self.FUNCTION_DICT = {'start': self.start, 'category': self.category,
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
            self.FUNCTION_DICT[state.split('-')[0]](text)

    def ask(self):
        pass

    def start(self, text):
        if text == 'хочу бота':
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
        self.client.hset(self.user_id, "category", text)
        self.client.hset(self.user_id, "now", 'char_1')
        keyboard = create_keyboard()
        self.vk.messages.send(user_id=self.user_id,
                              message='Пройдите опрос&#128196;',
                              random_id=random.randint(0, 2 ** 64),
                              keyboard=keyboard)
        keyboard = create_keyboard(
            buttons=[['Организация', VkKeyboardColor.PRIMARY],
                     ['Индивидуально', VkKeyboardColor.PRIMARY]], d=2,
            ask=False, inline=True)
        self.vk.messages.send(user_id=self.user_id,
                              message=f'Для кого?',
                              random_id=random.randint(0, 2 ** 64),
                              keyboard=keyboard)

    def char_1(self, text):
        if text in ['организация', 'индивидуально']:
            self.client.hset(self.user_id, "char_1", text)
            self.client.hset(self.user_id, "now", "accept")
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
            self.vk.messages.send(user_id=self.user_id,
                                  message='Кратко опишите вашу идею и  отправьте сообщение',
                                  random_id=random.randint(0, 2 ** 64))
        elif text.startswith('отменить'):
            self.client.hset(self.user_id, "now", 'start')
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
        self.client.hset(self.user_id, "comment", text)
        self.client.hset(self.user_id, "now", 'contact')
        keyboard = create_keyboard(
            buttons=[['Вконтакте', VkKeyboardColor.DEFAULT],
                     ['Email', VkKeyboardColor.DEFAULT],
                     ['Номер телефона', VkKeyboardColor.DEFAULT]], d=2)
        self.vk.messages.send(user_id=self.user_id,
                              message=f'Как нам с вами связаться?',
                              random_id=random.randint(0, 2 ** 64),
                              keyboard=keyboard)

    def contact(self, text):
        if text.startswith('вк'):
            self.client.hset(self.user_id, "contact", "ВК")
            self.client.hset(self.user_id, "now", 'manager-vk')
            return self.manager(text)
        elif text == 'email':
            self.client.hset(self.user_id, "contact", "EMAIL")
            self.client.hset(self.user_id, "now", 'manager-email')
            keyboard = create_keyboard(
                buttons=[])
            self.vk.messages.send(user_id=self.user_id,
                                  message='Введите ваш адрес email',
                                  random_id=random.randint(0, 2 ** 64),
                                  keyboard=keyboard)
        elif text.startswith('номер'):
            self.client.hset(self.user_id, "contact", "НОМЕР")
            self.client.hset(self.user_id, "now", 'manager-phone')
            keyboard = create_keyboard(
                buttons=[])
            self.vk.messages.send(user_id=self.user_id,
                                  message='Введите ваш номер телефона',
                                  random_id=random.randint(0, 2 ** 64),
                                  keyboard=keyboard)
        else:
            pass

    def manager(self, text):
        contact = self.client.hget(self.user_id, "now").decode('utf-8').split('-')[1]
        if contact == 'vk':
            self.btx.callMethod("crm.lead.add", fields={
                "TITLE": f"Заказ {self.vk.users.get(user_id=self.user_id)[0]['first_name']}{self.vk.users.get(user_id=self.user_id)[0]['last_name']}.Категория:{self.client.hget(self.user_id, 'category').decode('utf-8')}",
                "NAME": f"{self.vk.users.get(user_id=self.user_id)[0]['first_name']}",
                "LAST_NAME": f"{self.vk.users.get(user_id=self.user_id)[0]['last_name']}",
                "STATUS_ID": "NEW",
                "OPENED": "Y",
                "ASSIGNED_BY_ID": 1,
                "COMMENTS": f"Категория бота: {self.client.hget(self.user_id, 'category').decode('utf-8')}, для {self.client.hget(self.user_id, 'char_1').decode('utf-8')}\n Информация от заказчика:{self.client.hget(self.user_id, 'comment').decode('utf-8')}.\n Удобно связаться через {self.client.hget(self.user_id, 'contact').decode('utf-8')}"},
                                params={"REGISTER_SONET_EVENT": "Y"})
        elif contact == 'email':
            self.btx.callMethod("crm.lead.add", fields={
                "TITLE": f"Заказ {self.vk.users.get(user_id=self.user_id)[0]['first_name']}{self.vk.users.get(user_id=self.user_id)[0]['last_name']}.Категория:{self.client.hget(self.user_id, 'category').decode('utf-8')}",
                "NAME": f"{self.vk.users.get(user_id=self.user_id)[0]['first_name']}",
                "LAST_NAME": f"{self.vk.users.get(user_id=self.user_id)[0]['last_name']}",
                "STATUS_ID": "NEW",
                "OPENED": "Y",
                "ASSIGNED_BY_ID": 1,
                "COMMENTS": f"Категория бота: {self.client.hget(self.user_id, 'category').decode('utf-8')}, для {self.client.hget(self.user_id, 'char_1').decode('utf-8')}\n Информация от заказчика:{self.client.hget(self.user_id, 'comment').decode('utf-8')}.\n Удобно связаться через {self.client.hget(self.user_id, 'contact').decode('utf-8')}"},
                                params={"REGISTER_SONET_EVENT": "Y"})
        elif contact == 'phone':
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
            pass
            bitrix_bot = BitrixBot(vk, client, event.obj.message['from_id'], "hl76a3vhf7v1kloh")
            bitrix_bot.analyse_type(event.obj.message)


if __name__ == '__main__':
    main()
