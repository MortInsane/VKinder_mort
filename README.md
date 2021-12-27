# VKinder - это бот, который поможет найти тебе пару.

Поиск осуществляется на основе полученных данных профиля, 
если каких то данных недостаточно, бот их запросит.

## Получение vk токена(ключ доступа пользователя)
[Ссылка](https://vk.com/dev/implicit_flow_user) на получение токена vk

## Настройка группы и получение vk токена(ключ доступа группы)
[Ссылка](https://github.com/netology-code/py-advanced-diplom/blob/new_diplom/group_settings.md) на получение токена vk

## Настройка и запуск
1. переименуйте `.env.dist` в `.env`
2. заполните данные
``
VK_GROUP_TOKEN=...
VK_USER_TOKEN=...
VK_VERSION=...
POSTGRES_DB=...
POSTGRES_USER=...
POSTGRES_PASSWORD=...
IP=...
PORT=...
``
3. установите зависимости `pip install -r requirements.txt`
4. запустите `docker-compose up`
5. Запустите `app.py`
6. Напишите боту `Привет` и следуйте инструкциям в чате