# Сервис для извлечения юридической информации из дерева в форматах JSON и XML

## Установка и запуск
1. Создание виртуального окружения `python -m venv venv`
2. Активация виртуального окружения 
   * Windows `.\venv\Scripts\activate`
   * UNIX `source ./venv/bin/activate`
3. Установка зависимостей `python -m pip install -r requirements`
4. Запуск сервера `python manage.py runserver`

## Отправка запроса
* URL: /api/merge/ 
* Тип запроса: (POST)

### Примеры тела запроса в файлах `request.json` и `request.XML`