# dragee

## Установка

1. Скачайте webdriver для вашего браузера
1. Убедитесь, что у вас установлен python версии 3.7 или выше
1. Создайте и активируйте virtualenv
1. Установите необходимые пакеты командой
  `pip install -r requirements.txt`

## Настройка

Создайте файл .env и запишите туда следующие данные:

```
PHONE=номер телефона или логин
PWD=ваш пароль
APP_ID=7415460
GROUP_ID=id вашей группы
TOKEN=можно получить пройдя по ссылке https://oauth.vk.com/authorize?client_id=7415460&display=page&scope=wall,photos&response_type=token&v=5.103
USER_ID=id пользователя
```

В строке 36 файла worker.py:

`driver = webdriver.Edge('D:/Projects/msedgedriver.exe')`

- нужно заменить Edge на название вашего браузера
- скачать webdriver для вашей версии браузера
- заменить D:/Projects/msedgedriver.exe на путь к вашему драйверу
