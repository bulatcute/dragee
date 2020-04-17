import vk
import dotenv
import os
from collections import deque
from selenium import webdriver
from bs4 import BeautifulSoup as bs4
import time
from dataclasses import dataclass
import requests
import json

dotenv.load_dotenv()
TOKEN = os.environ['TOKEN']
GROUP_ID = os.environ['GROUP_ID']
APP_ID = os.environ['APP_ID']
LOGIN = os.environ['PHONE']
PASSWORD = os.environ['PWD']
USER_ID = os.environ['USER_ID']

queue = deque()

@dataclass()
class Post:
    title: str
    description: str
    gallery: list
    price: str
    district: str
    adress: str
    phone: str
    vk: str


def parse():
    driver = webdriver.Edge('D:/Projects/msedgedriver.exe')

    driver.get('https://arenda.dragee.ru/offer/list/')
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)

    soup = bs4(driver.page_source, features='html.parser')

    driver.quit()

    b_offers = soup.find_all('div', {'class': 'b-offer'})

    out = []

    for offer in b_offers:
        if ('Обновлено' in offer.find('div', {'class': 'b-offer__title-date i-inline'}).text
                or 'Собственник' not in offer.find('div', {'class': 'b-offer__owner-type'}).text):
            continue

        price = ' '.join(i.strip() for i in (offer.find('div', {'class': 'b-offer__price'}).text.strip(
        ) + offer.find('div', {'class': 'b-offer__price-comment'}).text.strip()).split())

        title = ' '.join([i.strip() for i in offer.find(
            'a', {'class': 'b-link b-offer__title i-inline'}).text.split()])

        adr = '\n'.join([i.strip() for i in offer.find(
            'div', {'class', 'b-offer__address'}).text.strip().split('\n') if i.strip()])
        adress, district = adr.split('\n')

        phone = offer.find('a', {'class': 'offer-mobile-phone'}).text

        try:
            vk = offer.find(
                'a', {'class': 'b-offer__link b-offer__vk-link'}).get('href')
        except:
            vk = None

        gallery_div = offer.find('div', {'class': 'b-offer__gallery'})
        gallery = ['https://arenda.dragee.ru' + a.get('href') for a in gallery_div.find_all('a')]

        content = offer.find('div', 'b-offer__content')
        description = content.text.replace('Показать полностью', '').strip()

        out.append(Post(title, description, gallery,
                        price, district, adress, phone, vk))
    return out


def sender():
    while True:
        try:
            wall_post = queue.pop()
        except:
            break

        session = vk.AuthSession(scope='wall,photos', app_id=int(
            APP_ID), access_token=TOKEN, user_login=LOGIN, user_password=PASSWORD)
        api = vk.API(session, v='5.103')
        destination = api.photos.getWallUploadServer(gid=GROUP_ID)

        attachments = []

        for url in wall_post.gallery:
            image = requests.get(url, stream=True, verify=False)
            data = ("image.jpg", image.content)
            meta = requests.post(destination['upload_url'], files={'photo': data})
            result = json.loads(meta.text)
            photo = api.photos.saveWallPhoto(photo=result['photo'], hash=result['hash'], server=result['server'], gid=GROUP_ID)
            photo = photo[0]
            attachments.append(f'photo{USER_ID}_{photo["id"]}')
        
        mess_me = f'\nНаписать мне: {wall_post.vk}' if wall_post.vk else ''

        api.wall.post(owner_id='-' + GROUP_ID,
                    message=f'''Понравилась квартира? Сделай РЕПОСТ вдруг её ищут твои друзья

Я: Собственник
Сдаётся: {wall_post.title}
Цена: {wall_post.price}
Район: {wall_post.district}
Адрес: {wall_post.adress}
Дополнительно: {wall_post.description}

Пожалуйста, скажите, что узнали об объявлении в группе "De_mall"
Позвонить мне: {wall_post.phone}{mess_me}
Если при обращение к арендодателю с вас попросили комиссию или информация не совпадает с указанной, отправьте ссылку на объявление Администратору https://vk.com/id476040447 он проверит его еще раз!
#Арендаквартир #Снятьквартиру #Снятьоднокомнатнуюквартиру #Снятьдвухкомнатнуюквартиру #Снятьтрехкомнатнуюквартиру #Арендакомнаты #Снятькомнату #Сдатькомнату #Сдатьоднокомнатнуюквартиру #Сдатьдвухкомнатнуюквартиру #Сдатьтрехкомнатнуюквартиру''', 
                  attachments=attachments)


def getter():
    for post in parse():
        if post not in queue:
            queue.append(post)
        if len(queue) > 50:
            queue.popleft()


if __name__ == "__main__":
    getter()
    sender()
