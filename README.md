# csv_checker
Проверяет папку 'IN_FOLDER' на наличие файлов в формате csv.


Пример имени файла: 

`'20210102_1234_DME.csv' - '<год><месяц><день>_<номер рейса>_<аэропорт вылета>.csv'`

Пример содержимого файла:
```
num;surname;firstname;bdate
1;IVANOV;IVAN;11NOV73
2;PETROV;ALEXANDER;13JUL79
3;BOSHIROV;RUSLAN;12APR78
```

Далее файл преобразуется в формат json и сохраняется в папке 'OUT_FOLDER'.

Исходный файл перемещается в папку 'OK_FOLDER'.

В случае возникновения ошибок файл перемещается в папку 'ERR_FOLDER'.

Одновременно с этим создается запись в таблице 'flight' базы данных PostgreSQL посредством SQLAlchemy.
## Инструкция

* Установить requirements.txt
* Создать пользователя и базу данных в PostgreSQL
* Заполнить файл settings.py полученными данными.

### Запуск:
* `python script.py`

## Requirements
- Python 3.10
- PostgreSQL
- SQLAlchemy