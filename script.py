import os
import sys
import time

from loguru import logger

from services.db import DataBaseManager
from settings import *
from services.csv_utils import parser_name_csv, csv_to_json

BASE_DIR = os.getcwd()

logger.remove()
logger.add(sys.stdout, format=log_format)


def check_folders(*folders: str):
    """Проверка на наличии папок и создание"""
    for folder in folders:
        if not os.path.exists(folder):
            try:
                os.mkdir(folder)
            except OSError:
                logger.error(f'Создать директорию {folder} не удалось.')
                sys.exit(1)
            else:
                logger.success(f'Успешно создана директория {folder}.')


def move_file(from_: str, to: str, filename: str) -> None:
    """Перемещение файла из папки в папку"""
    os.replace(os.path.join(BASE_DIR, from_, filename), os.path.join(BASE_DIR, to, filename))
    logger.info(f'Файл {filename} перемещен из папки {from_} в папку {to}.')


def main():
    check_folders(IN_FOLDER, OUT_FOLDER, OK_FOLDER, ERR_FOLDER)

    # Подключаем базу данных
    database = DataBaseManager(dbname, user, password, host, table_name='flight')
    database.create_table()

    # Просматриваем папку IN_FOLDER на наличие файлов
    while True:
        for csvFile in os.listdir(IN_FOLDER):
            data_from_filename = parser_name_csv(csvFile)
            if data_from_filename is None:
                move_file(IN_FOLDER, ERR_FOLDER, csvFile)
            else:
                jsonFile = csv_to_json(os.path.join(IN_FOLDER, csvFile), data_from_filename, OUT_FOLDER)
                if jsonFile is None:
                    move_file(IN_FOLDER, ERR_FOLDER, csvFile)
                else:
                    move_file(IN_FOLDER, OK_FOLDER, csvFile)
                    values = (csvFile,
                              int(data_from_filename['flt']),
                              data_from_filename['date'],
                              data_from_filename['dep'])
                    database.insert_values(values)
        time.sleep(60)


if __name__ == '__main__':
    params = (dbname, user, password, host, IN_FOLDER, OUT_FOLDER, OK_FOLDER, ERR_FOLDER)
    if not all(params):
        logger.error('Проверьте правильность ввода информации в файл settings.py.')
        sys.exit(1)
    main()
