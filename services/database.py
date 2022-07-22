import sys
from loguru import logger
from sqlalchemy import create_engine, inspect, Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

TABLE_NAME = 'flight'
Base = declarative_base()


class Flight(Base):
    """Таблица рейсов"""
    __tablename__ = TABLE_NAME

    id = Column(Integer, primary_key=True)
    file_name = Column(String, nullable=False)
    flt = Column(Integer, nullable=False)
    depdate = Column(Date, nullable=False)
    dep = Column(String, nullable=False)

    def __repr__(self):
        return f'{self.depdate} - {self.flt} - {self.dep}'


class DataBaseManager:
    """Взаимодействует с базой PosgreSQL"""

    def __init__(self, dbname, user, password, host):
        self.dbname = dbname
        self.user = user
        self._password = password
        self.host = host
        self.transaction_status = False
        self.engine = self._get_engine()
        self._create_table()

    def _get_engine(self):
        """Подключение к базе данных"""
        try:
            return create_engine(f'postgresql+psycopg2://{self.user}:{self._password}@{self.host}/{self.dbname}')
        except Exception as err:
            logger.error(f"Не удалось подключиться к базе данных: {self.dbname}")
            logger.error(err)
            sys.exit(1)

    def insert_values(self, values: dict) -> None:
        """Вставка данных в таблицу"""
        try:
            Session = sessionmaker(bind=self.engine)
            with Session.begin() as session:
                session.add(Flight(**values))
            logger.success(f'Данные добавлены в таблицу {TABLE_NAME}.')
            self.transaction_status = True
        except Exception as err:
            logger.error(err)
            logger.error(f'Не удалось добавить данные в таблицу {TABLE_NAME}. \nДанные: {values}')
            self.transaction_status = False

    def _create_table(self) -> None:
        """Создание таблицы"""
        if not self._is_table_exists(TABLE_NAME):
            Base.metadata.create_all(self.engine)
            logger.success(f'Таблица {TABLE_NAME} создана.')
        else:
            ans = input(f'Таблица {TABLE_NAME} уже существует. Необходимо пересоздать. Продолжить?(Y/N):')
            if ans.strip().lower() == 'y':
                Base.metadata.drop_all(self.engine)
                Base.metadata.create_all(self.engine)
                logger.success(f'Таблица {TABLE_NAME} удалена и заново создана.')
            else:
                logger.error(f'Завершение, так как таблица {TABLE_NAME} уже существует.')
                sys.exit(1)

    def _is_table_exists(self, name: str) -> bool:
        """Проверка наличия таблицы в базе данных"""
        return inspect(self.engine).has_table(name)
