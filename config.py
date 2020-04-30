with open('.env', 'wt') as pydotenv:
    towrite = {
        'PHONE': input('Введите номер телефона от аккаунта вк в формате +79ХХХХХХХХХ\n> '),
        'PWD': input('Введите пароль от вк\n> '),
        'GROUP_ID': input('Введите id вашей группы (можно получить по ссылке https://regvk.com/id/)\n> '),
        'USER_ID': input('Введите id пользователя вк (можно получить по ссылке https://regvk.com/id/)\n> '),
        'TOKEN': input('Пройдите по ссылке ххх и вставьте токен из адресной строки\n> ')
    }
    for key, value in towrite.items():
        pydotenv.write(f'{key}={value}\n')