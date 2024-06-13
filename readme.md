Для запуска приложения выполните следующие шаги:
Установите зависимости:
    pip install -r requirements.txt

Инициализируйте базу данных:
    flask db init
    flask db migrate -m "Initial migration."
    flask db upgrade

Запустите приложение:
    flask run