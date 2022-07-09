import sys
import psycopg2
import psycopg2.extras
from loguru import logger


class DataBaseManager:
    """Взаимодействует с базой PosgreSQL"""
    TABLE_NAME = 'flight'

    def __init__(self, dbname, user, password, host, table_name=None):
        self.dbname = dbname
        self.user = user
        self._password = password
        self.host = host
        if table_name:
            self.TABLE_NAME = table_name
        self.connection = self._get_connection()

    def create_table(self):
        """Создание таблицы"""
        CREATE_TABLE = f"""CREATE TABLE {self.TABLE_NAME}(
                        id SERIAL primary key,
                        file_name text not null,
                        flt int not null,
                        depdate date not null,
                        dep text not null );"""

        with self.connection.cursor() as cursor:
            if not self._is_table_exists(cursor):
                self._sql_execute(cursor, CREATE_TABLE)
                logger.success(f'Таблица {self.TABLE_NAME} создана.')
            else:
                ans = input(f'Таблица {self.TABLE_NAME} уже существует. Необходимо пересоздать. Продолжить?(Y/N):')
                if ans.strip().lower() == 'y':
                    self._sql_execute(cursor, f"""DROP TABLE {self.TABLE_NAME};""" + CREATE_TABLE)
                    logger.success(f'Таблица {self.TABLE_NAME} удалена и заново создана.')
                else:
                    logger.error(f'Завершение, так как таблица {self.TABLE_NAME} уже существует.')
                    self._close_connection()
                    sys.exit(1)

    def insert_values(self, values: tuple):
        """Вставка данных в таблицу"""
        with self.connection.cursor() as cursor:
            query = f"INSERT INTO {self.TABLE_NAME} (file_name, flt, depdate, dep) VALUES (%s,%s,%s,%s)"
            try:
                cursor.execute(query, values)
                logger.success(f'Данные добавлены в таблицу {self.TABLE_NAME}.')
            except Exception as err:
                logger.error(err)
                logger.error(f'Не удалось добавить данные в таблицу {self.TABLE_NAME}. \nДанные: {values}')

    def _get_connection(self):
        """Подключение к базе данных"""
        try:
            connection = psycopg2.connect(
                host=self.host,
                user=self.user,
                password=self._password,
                database=self.dbname
            )
            connection.autocommit = True
            return connection
        except Exception as err:
            logger.error(f"Не удалось подключиться к базе данных: {self.dbname}")
            logger.error(err)
            sys.exit(1)

    def _close_connection(self):
        """Закрывает соединение с базой данных"""
        if getattr(self, 'connection'):
            self.connection.close()
            logger.info("Соединение с базой данных закрыто.")

    def _is_table_exists(self, cursor) -> bool:
        """Проверка наличия таблицы"""
        self._sql_execute(cursor, f"SELECT EXISTS(SELECT relname FROM pg_class WHERE relname = '{self.TABLE_NAME}');")
        return True if cursor.fetchone()[0] else False

    def _sql_execute(self, cursor, query: str):
        """Выполнение SQL запроса"""
        try:
            cursor.execute(query)
        except Exception as err:
            logger.error(f'Неудачное выполнение SQL запроса в таблицу {self.TABLE_NAME}.')
            logger.error(err)
            self._close_connection()
