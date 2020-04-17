# dragee

Для того, чтобы скрипт работал, необходимо в папке с ним создать файл .env и прописать в него следующие параметры:

```
PHONE=номер телефона или пароль
PWD=ваш пароль
APP_ID=7415460
GROUP_ID=id вашей группы
TOKEN=можно получить пройдя по ссылке https://oauth.vk.com/authorize?client_id=7415460&display=page&scope=wall,photos&response_type=token&v=5.103
USER_ID=id пользователя
```

В строке 35 файла worker.py:

`driver = webdriver.Edge('D:/Projects/msedgedriver.exe')`

- нужно заменить Edge на название нашего браузера
- скачать webdriver для вашей версии браузера
- заменить D:/Projects/msedgedriver.exe на путь к вашему драйверу