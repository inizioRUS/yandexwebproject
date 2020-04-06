from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def create_keyboard(buttons=None, inline=False, location=False,
                    geo=False, one_time=False, d=3):
    keyboard = VkKeyboard(one_time=one_time, inline=inline)
    line = False
    if geo:
        keyboard.add_location_button()
        keyboard.add_line()
    if not location:
        for i in range(len(buttons) // d):
            for j in range(d):
                keyboard.add_button(buttons[i * d + j][0],
                                    color=buttons[i * d + j][1])
            keyboard.add_line()
        for i in range(len(buttons) % d):
            keyboard.add_button(buttons[- i - 1][0],
                                color=buttons[- i - 1][1])
            line = True
        if line:
            keyboard.add_line()
        keyboard.add_button('Вернуться на главную',
                            color=VkKeyboardColor.NEGATIVE)
    else:
        keyboard.add_location_button()
    return keyboard.get_keyboard()