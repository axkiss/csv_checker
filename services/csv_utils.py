import os
import re
import csv
import json
from loguru import logger
from datetime import datetime


def parser_name_csv(csv_file: str) -> dict | None:
    """Проверка на валидность и парсинг данных из имени файла"""
    filename, file_extension = os.path.splitext(csv_file)
    if file_extension not in ('.csv', '.CSV'):
        logger.warning(f'Файл {csv_file} имеет неверное расширение.')
        return None

    # Проверяем валидность названия файла
    raw_data = filename.split('_')
    if len(raw_data) != 3:
        logger.warning(f'Файл {csv_file} имеет некорректное название.')
        return None

    date = raw_data[0]
    if len(date) != 8:
        logger.warning(f'Файл {csv_file} имеет неверную "дату" {date} в названии.')
        return None
    else:
        try:
            date = datetime.strptime(raw_data[0], '%Y%m%d')
            date = datetime.strftime(date, '%Y-%m-%d')
        except ValueError:
            logger.warning(f'Файл {csv_file} имеет неверную "дату" {date} в названии.')
            return None

    #  Считаем, что номер рейса содержит всегда 4 цифры
    flight_number = raw_data[1]
    if not re.fullmatch('^\d{4}$', flight_number):
        logger.warning(f'Файл {csv_file} имеет неверный "номер рейса" {flight_number} в названии.')
        return None

    #  Считаем, что аэропорт вылета может состоять только из трех заглавных букв
    departure_airport = raw_data[2]
    if not re.fullmatch('^[A-Z]{3}$', departure_airport):
        logger.warning(f'Файл {csv_file} имеет неверный "аэропорт вылета" {departure_airport} в названии.')
        return None

    return {'date': date, 'flt': flight_number, 'dep': departure_airport}


def csv_to_json(csv_file_path: str, data_from_filename: dict, folder_to_save: str) -> str | None:
    """Проверяет данные из CSV и сериализует их в JSON"""
    data_form_csv = []
    # Получим данные из CSV
    with open(csv_file_path, encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf, delimiter=';')
        fields = csvReader.fieldnames

        for row in csvReader:
            if row.get(None, None):
                logger.warning(f'Файл {csv_file_path} некорректен. Колонок меньше, чем данных.')
                return None

            # Проверяем каждое поле в строчке
            for field in fields:
                # Проверка на пустые значения
                if row[field] is None or row[field] == '':
                    logger.warning(f'Файл {csv_file_path} некорректен. Содержит пустые значения.')
                    return None
                # Проверка на корректную дату
                if field == 'bdate':
                    if len(row[field]) != 7:
                        logger.warning(f'Файл {csv_file_path} имеет поле с неверной датой {row[field]}.')
                        return None
                    else:
                        try:
                            date = datetime.strptime(row[field], '%d%b%y')
                            row[field] = datetime.strftime(date, '%Y-%m-%d')
                        except ValueError:
                            logger.warning(f'Файл {csv_file_path} имеет поле с неверной датой {row[field]}.')
                            return None
            data_form_csv.append(row)
    if not data_form_csv:
        logger.warning(f'Файл {csv_file_path} не содержит данных.')
        return None

    csv_file = os.path.basename(csv_file_path)
    filename, file_extension = os.path.splitext(csv_file)
    json_file_path = os.path.join(folder_to_save, filename + '.json')
    # Сформируем словарь из данных имени и содержимого CSV
    data_to_json = {**data_from_filename, 'prl': data_form_csv}
    # Создание JSON файла с данными
    with open(json_file_path, 'w', encoding='utf-8') as jsonf:
        jsonf.write(json.dumps(data_to_json))

    logger.success(f'Файл {json_file_path} создан.')
    return json_file_path
