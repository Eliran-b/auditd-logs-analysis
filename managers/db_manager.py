import logging
from contextlib import contextmanager
from typing import Any
import sqlalchemy
from models import Base, User
from utils.db_connector import DBConnector
from utils.singleton import Singleton


class DBManager(metaclass=Singleton):
    db_connector: DBConnector

    def __new__(cls):
        cls.db_connector = DBConnector()
        cls._create_database_schema()
        return super().__new__(cls)

    @classmethod
    def _create_database_schema(cls):
        try:
            Base.metadata.create_all(cls.db_connector.engine)
            users_data = [{"id": "1000", "name": "eliran"}, {"id": "2000", "name": "test_user"}]
            for user in users_data:
                with cls.writer_session() as session:
                    if session.query(User).filter_by(id=user["id"]).first() is None:
                        new_user = User(**user)
                        session.add(new_user)

        except Exception as e:
            logging.error(f"Error creating database schema: {e}")
            raise

    @classmethod
    def run_raw_sql_query(cls, sql_query: str, fetch_one: bool = False) -> Any:
        with cls.db_connector.engine.connect() as connection:
            logging.info(f"executing query {sql_query}")
            result = connection.execute(sqlalchemy.text(sql_query))
            if fetch_one:
                return result.cursor.fetchone()
            return result.cursor.fetchall()

    @classmethod
    def run_raw_sql_query_with_mapped_result(cls, sql_query: str):
        with cls.db_connector.engine.connect() as connection:
            result_proxy = connection.execute(sqlalchemy.text(sql_query))

            # Get the column names from the result set
            column_names = result_proxy.keys()

            # Fetch all rows from the result set
            results = result_proxy.fetchall()

            return [dict(zip(column_names, res)) for res in results]

    @classmethod
    @contextmanager
    def reader_session(cls):
        current_session = cls.db_connector.session()
        try:
            yield current_session
        finally:
            current_session.close()
    
    @classmethod
    @contextmanager
    def writer_session(cls):
        current_session = cls.db_connector.session()
        try:
            yield current_session
            current_session.commit()
        except Exception as e:
            logging.error(f"Could not commit {e}")
            current_session.rollback()
            raise
        finally:
            current_session.close()

    @classmethod
    def insert_bulk(cls, data_model_list: list[dict], model_class: Base):
        try:
            logging.info(f"inserting to {model_class.__tablename__} bulk: {data_model_list}")
            with cls.writer_session() as session:
                session.bulk_save_objects(data_model_list)
        except Exception as e:
            logging.error(f"Error insert table {model_class.__tablename__} logs bulk: {e}")
            raise

    @classmethod
    def load_model_query_result(cls, model_class: Base, row: [tuple, None]) -> Base:
        # Get the column names
        column_names = [column.name for column in model_class.__table__.columns]

        # Create a dictionary with column names and corresponding values
        try:
            return model_class(**dict(zip(column_names, row)))
        except TypeError:
            return None

    @staticmethod
    def get_model_index_name(model_class: Base, column_object: sqlalchemy.orm.attributes.InstrumentedAttribute):
        for index in model_class.__table__.indexes:
            if index.name.endswith(column_object.name):
                return index.name
        raise ValueError(f"there is no index name for column {column_object.name} in table {model_class.__tablename__}")
