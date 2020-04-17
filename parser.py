from selenium import webdriver
from bs4 import BeautifulSoup as bs4
import time
from dataclasses import dataclass


@dataclass()
class Post:
    title: str
    description: str
    gallery: list
    price: str
    price_comment: str
    district: str
    adress: str
    phone: str
    vk: str


def parse():
    driver = webdriver.Edge('D:/Projects/msedgedriver.exe')

    driver.get('https://arenda.dragee.ru/offer/list/')

    soup = bs4(driver.page_source, features='html.parser')

    driver.quit()

    b_offers = soup.find_all('div', {'class': 'b-offer'})

    out = []

    for offer in b_offers:
        if ('Обновлено' in offer.find('div', {'class': 'b-offer__title-date i-inline'}).text
                or 'Собственник' not in offer.find('div', {'class': 'b-offer__owner-type'}).text):
            continue

        price = offer.find('div', {'class': 'b-offer__price'}).text.strip()
        price_comment = offer.find('div',
                                   {'class': 'b-offer__price-comment'}).text.strip()

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
        gallery = [a.get('href') for a in gallery_div.find_all('a')]

        content = offer.find('div', 'b-offer__content')
        description = content.text.replace('Показать полностью', '').strip()

        out.append(Post(title, description, gallery, price,
                        price_comment, district, adress, phone, vk))
    return out

for i in parse():
    print(i)
