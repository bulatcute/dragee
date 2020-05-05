import asyncio
import datetime
import json
import os
import time
from collections import deque
from dataclasses import dataclass

import dotenv
import requests
import vk
from bs4 import BeautifulSoup as bs4
from selenium import webdriver

dotenv.load_dotenv()
TOKEN = os.environ['TOKEN']
GROUP_ID = os.environ['GROUP_ID']
APP_ID = os.environ['APP_ID']
LOGIN = os.environ['PHONE']
PASSWORD = os.environ['PWD']
USER_ID = os.environ['USER_ID']

queue = deque()
last_id = 129389


@dataclass()
class Post:
    id_: int
    title: str
    description: str
    gallery: list
    price: str
    district: str
    adress: str
    phone: str
    vk: tuple


def parse():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome('D:/Projects/chromedriver.exe', options=options)

    driver.get('https://arenda.dragee.ru/offer/list/')

    soup = bs4(driver.page_source, features='html.parser')

    driver.quit()

    b_offers = soup.find_all('div', {'class': 'b-offer'})

    out = []

    session = vk.Session()
    api = vk.API(session, v='5.103')

    global last_id

    for offer in b_offers:
        if ('Обновлено' in offer.find('div', {'class': 'b-offer__title-date i-inline'}).text
                or 'Собственник' not in offer.find('div', {'class': 'b-offer__owner-type'}).text):
            continue
        id_ = offer.find('div', {'class': 'b-offer__title-block'}).find(
            'a').get('href').split('/')[-2]
        id_ = int(id_)
        if id_ <= last_id:
            continue

        price = ' '.join(i.strip() for i in (offer.find('div', {'class': 'b-offer__price'}).text.strip(
        ) + offer.find('div', {'class': 'b-offer__price-comment'}).text.strip()).split())

        title = ' '.join([i.strip() for i in offer.find(
            'a', {'class': 'b-link b-offer__title i-inline'}).text.split()])

        adr = '\n'.join([i.strip() for i in offer.find(
            'div', {'class', 'b-offer__address'}).text.strip().split('\n') if i.strip()])
        adress, district = adr.split('\n')

        try:
            owner = offer.find(
                'div', {'class', 'b-offer__owner-name'}).text.strip()
        except:
            owner = None

        try:
            phone = offer.find('a', {'class': 'offer-mobile-phone'}).text
        except:
            phone = None

        phone = phone + ' — ' + owner if phone and owner else phone

        try:
            user_vk = offer.find(
                'a', {'class': 'b-offer__link b-offer__vk-link'}).get('href')
            r = api.users.get(access_token=TOKEN,
                              user_ids=user_vk.split('/')[-1])
            first_name = r[0]['first_name']
            last_name = r[0]['last_name']
            user_vk = (user_vk, f'{first_name} {last_name}')
        except AttributeError:
            user_vk = None

        gallery_div = offer.find('div', {'class': 'b-offer__gallery'})
        gallery = ['https://arenda.dragee.ru' +
                   a.get('href') for a in gallery_div.find_all('a')]

        content = offer.find('div', 'b-offer__content')
        description = content.text.replace('Показать полностью', '').strip()

        out.append(Post(id_, title, description, gallery[1:],
                        price, district, adress, phone, user_vk))
    last_id = max([post.id_ for post in out]) if out else last_id
    print(f'получены данные о {len(out)} постах')
    return out[::-1]


async def sender():
    while True:
        if datetime.datetime.now().hour >= 16 or datetime.datetime.now().hour <= 4:
            await asyncio.sleep(3600)
            continue
        try:
            print('пытаюсь получить пост')
            wall_post = queue.popleft()
        except:
            print('пост не получен')
            await asyncio.sleep(60)
            continue
        print('пост получен')

        session = vk.AuthSession(scope='wall,photos', app_id=int(
            APP_ID), access_token=TOKEN, user_login=LOGIN, user_password=PASSWORD)
        api = vk.API(session, v='5.103')
        destination = api.photos.getWallUploadServer(gid=GROUP_ID)

        attachments = []

        for url in wall_post.gallery:
            image = requests.get(url, stream=True, verify=False)
            data = ("image.jpg", image.content)
            meta = requests.post(
                destination['upload_url'], files={'photo': data})
            result = json.loads(meta.text)
            photo = api.photos.saveWallPhoto(
                photo=result['photo'], hash=result['hash'], server=result['server'], gid=GROUP_ID)
            photo = photo[0]
            attachments.append(f'photo{USER_ID}_{photo["id"]}')

        mess_me = f'\nНаписать мне: @{wall_post.vk[0]} ({wall_post.vk[1]})' if wall_post.vk else ''
        call_me = f'\nПозвонить мне: {wall_post.phone}' if wall_post.phone else ''

        api.wall.post(owner_id='-' + GROUP_ID,
                      message=f'''Понравилась квартира? Сделай РЕПОСТ вдруг её ищут твои друзья

Я: Собственник
Сдаётся: {wall_post.title}
Цена: {wall_post.price}
Район: {wall_post.district}
Адрес: {wall_post.adress}
Дополнительно: {wall_post.description}

Пожалуйста, скажите, что узнали об объявлении в группе "ИНФОМИР"
{call_me}{mess_me}

Если при обращение к арендодателю с вас попросили комиссию или информация не совпадает с указанной, отправьте ссылку на объявление Администратору https://vk.com/id590803836 он проверит его еще раз!

#Арендаквартир #Снятьквартиру #Снятьоднокомнатнуюквартиру #Снятьдвухкомнатнуюквартиру #Снятьтрехкомнатнуюквартиру #Арендакомнаты #Снятькомнату #Сдатькомнату #Сдатьоднокомнатнуюквартиру #Сдатьдвухкомнатнуюквартиру #Сдатьтрехкомнатнуюквартиру''',
                      attachments=attachments)
        print('post sent')
        await asyncio.sleep(60)


async def getter():
    while True:
        for post in parse():
            print(post)
            queue.append(post)
            print('добавлено в очередь')
        await asyncio.sleep(120)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(getter())
    loop.create_task(sender())
    loop.run_forever()
