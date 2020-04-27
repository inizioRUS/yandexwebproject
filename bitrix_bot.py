import random

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


class BitrixBot:
    def __init__(self, vk, client, id):
        self.vk = vk
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
            self.client.set(self.user_id, 'start')
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
                state = self.client.get(self.user_id).decode('utf-8')
            except Exception:
                state = 'start'
                self.client.set(self.user_id, "start")
            logging.info(state)
            self.FUNCTION_DICT[state.split('-')[0]](text)

    def ask(self):
        pass

    def start(self, text):
        if text == 'хочу бота':
            self.client.set(self.user_id, "category")
            keyboard = create_keyboard(
                buttons=[['Чат-бот', VkKeyboardColor.DEFAULT],
                         ['Бот-игра', VkKeyboardColor.DEFAULT],
                         ['Бот-автоответчик', VkKeyboardColor.DEFAULT]], d=2)
            self.vk.messages.send(user_id=self.user_id,
                                  message=f'Выберите категорию бота (или укажите свою)&#128221;',
                                  random_id=random.randint(0, 2 ** 64),
                                  keyboard=keyboard)

    def category(self, text):
        self.client.set(self.user_id, "char_1")
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
            self.client.set(self.user_id, "accept")
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
            self.client.set(self.user_id, "description")
            keyboard = create_keyboard(
                buttons=[['Продолжить', VkKeyboardColor.PRIMARY]])
            self.vk.messages.send(user_id=self.user_id,
                                  message='Кратко опишите вашу идею и нажмите "продолжить"',
                                  random_id=random.randint(0, 2 ** 64),
                                  keyboard=keyboard)
        elif text.startswith('отменить'):
            self.client.set(self.user_id, 'start')
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
        if text == 'продолжить':
            self.client.set(self.user_id, "contact")
            keyboard = create_keyboard(
                buttons=[['Вконтакте', VkKeyboardColor.DEFAULT],
                         ['Email', VkKeyboardColor.DEFAULT],
                         ['Номер телефона', VkKeyboardColor.DEFAULT]], d=2)
            self.vk.messages.send(user_id=self.user_id,
                                  message=f'Как нам с вами связаться?',
                                  random_id=random.randint(0, 2 ** 64),
                                  keyboard=keyboard)
        else:
            pass

    def contact(self, text):
        if text.startswith('вк'):
            self.client.set(self.user_id, "manager-vk")
            return self.manager(text)
        elif text == 'email':
            self.client.set(self.user_id, "manager-email")
            keyboard = create_keyboard(
                buttons=[])
            self.vk.messages.send(user_id=self.user_id,
                                  message='Введите ваш адрес email',
                                  random_id=random.randint(0, 2 ** 64),
                                  keyboard=keyboard)
        elif text.startswith('номер'):
            self.client.set(self.user_id, "manager-phone")
            keyboard = create_keyboard(
                buttons=[])
            self.vk.messages.send(user_id=self.user_id,
                                  message='Введите ваш номер телефона',
                                  random_id=random.randint(0, 2 ** 64),
                                  keyboard=keyboard)
        else:
            pass

    def manager(self, text):
        contact = self.client.get(self.user_id).decode('utf-8').split('-')[1]
        if contact == 'vk':
            pass
        elif contact == 'email':
            pass
        elif contact == 'phone':
            pass
        self.client.set(self.user_id, 'start')
        keyboard = create_keyboard(
            buttons=[['Хочу бота', VkKeyboardColor.POSITIVE]])
        self.vk.messages.send(user_id=self.user_id,
                              message=f'В течении следующего часа с вами свяжется менеджер для оговорения стоимости и сроков сдачи.\nОжидайте...',
                              random_id=random.randint(0, 2 ** 64),
                              keyboard=keyboard)


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
            bitrix_bot = BitrixBot(vk, client, event.obj.message['from_id'])
            bitrix_bot.analyse_type(event.obj.message)


if __name__ == '__main__':
    main()
