from sqlalchemy import create_engine
from sqlalchemy.orm.session import Engine
from config import Config
from utils.singleton import Singleton
from sqlalchemy.orm import sessionmaker


class DBConnector(metaclass=Singleton):
    engine: Engine
    session: sessionmaker

    def __new__(cls):
        cls.engine = create_engine(f'sqlite:///{Config.DB_FILE_NAME}', echo=True)
        cls.session = sessionmaker(bind=cls.engine)
        return super().__new__(cls)
