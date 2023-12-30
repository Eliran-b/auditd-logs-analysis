from configparser import ConfigParser
from utils.singleton import Singleton


class Config(metaclass=Singleton):
    DB_FILE_NAME: str
    LOGS_FOLDER_NAME: str

    def __new__(cls, *args, **kwargs):
        config = ConfigParser()
        config.read('config.ini')
        cls.DB_FILE_NAME = config.get('Database', 'file')
        cls.LOGS_FOLDER_NAME = config.get('Logs', 'folder')
        return super().__new__(cls)
