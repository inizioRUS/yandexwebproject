import os
from datetime import datetime

import vk_api


def auth_handler():
    """ При двухфакторной аутентификации вызывается эта функция. """

    # Код двухфакторной аутентификации,
    # который присылается по смс или уведомлением в мобильное приложение
    key = input("Enter authentication code: ")
    # Если: True - сохранить, False - не сохранять.
    remember_device = True

    return key, remember_device


def get_photo_id():
    login, password = LOGIN, PASSWORD
    vk_session = vk_api.VkApi(login, password, auth_handler=auth_handler)
    try:
        vk_session.auth(token_only=True)
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return
    vk = vk_session.get_api()
    photos = vk.photos.get(album_id=int(input('album id: ')), group_id=int(input('group id: ')))
    for item in photos['items']:
        print(item['sizes'][-1]['url'], 'width:', item['sizes'][-1]['width'], 'height:', item['sizes'][-1]['height'])



if __name__ == '__main__':
    LOGIN, PASSWORD = '89372583764', 'житькайф'
    main()