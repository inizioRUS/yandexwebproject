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


def main():
    login, password = LOGIN, PASSWORD
    vk_session = vk_api.VkApi(login, password, auth_handler=auth_handler)
    try:
        vk_session.auth(token_only=True)
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return
    vk = vk_session.get_api()
    files = os.listdir('static/img')
    upload = vk_api.VkUpload(vk_session)
    for name in files:
        photo = upload.photo('static/img/' + name, int(input('Введите id альбома: ')))
        vk_photo_id = f"photo{photo[0]['owner_id']}_{photo[0]['id']}"
        vk = vk_session.get_api()
        vk.wall.post(message="Test", attachments=[vk_photo_id])



if __name__ == '__main__':
    LOGIN, PASSWORD = '89372583764', 'житькайф'
    main()