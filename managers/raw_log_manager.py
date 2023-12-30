import hashlib
import logging
from datetime import datetime

import sqlalchemy.orm.attributes
from managers.db_manager import DBManager
from models import RawLog


class RawLogManager(DBManager):

    @classmethod
    def get_last_raw_log_item(cls) -> [RawLog, None]:
        try:
            create_time_index_name = cls._get_index_name(RawLog.create_time)
            order_by_query = f"""SELECT * FROM raw_logs INDEXED BY {create_time_index_name}
                             ORDER BY create_time DESC, line_number DESC, log_file_path DESC LIMIT 1"""
            query_result = cls.run_raw_sql_query(order_by_query, fetch_one=True)
            return cls.load_query_result(query_result)
        except Exception as e:
            logging.error(f"Error getting last entry ID: {e}")
            return None

    @classmethod
    def _get_index_name(cls, column_object: sqlalchemy.orm.attributes.InstrumentedAttribute) -> str:
        return cls.get_model_index_name(model_class=RawLog, column_object=column_object)

    @classmethod
    def get_new_raw_logs_list(cls) -> list:
        sql_query = """
                    SELECT *
                    FROM raw_logs
                    WHERE create_time > COALESCE((SELECT MAX(create_time) FROM parsed_logs), '0000-00-00 00:00:00');
        """
        return cls.run_raw_sql_query(sql_query)

    @classmethod
    def insert_raw_logs_list(cls, raw_logs_data: dict[str: list[str]], start_line_number: int, run_time: datetime):
        try:
            serialized_raw_logs_list = cls.serialize_raw_logs_data(raw_logs_data, start_line_number, run_time)
            if serialized_raw_logs_list:
                cls.insert_bulk(data_model_list=serialized_raw_logs_list, model_class=RawLog)
        except Exception as e:
            logging.error(f"Error inserting new logs flow: {e}")
            raise

    @staticmethod
    def generate_raw_log_hash_id(log_content: str) -> str:
        return hashlib.sha256(log_content.encode()).hexdigest()

    @classmethod
    def serialize_raw_logs_data(cls, raw_logs_data: dict[str: list[str]], start_line_number: int,
                                run_time: datetime) -> list[dict]:
        result = []
        for log_file_path, raw_logs_list in raw_logs_data.items():
            for i, content in enumerate(raw_logs_list[start_line_number:], start=start_line_number):
                result.append(RawLog(content=content,
                                     log_file_path=log_file_path,
                                     line_number=i,
                                     run_time=run_time,
                                     hash_id=cls.generate_raw_log_hash_id(content),
                                     ))
            start_line_number = 0
        return result

    @classmethod
    def load_query_result(cls, row: [tuple, None]) -> RawLog:
        return super().load_model_query_result(model_class=RawLog, row=row)
