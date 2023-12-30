import logging
from managers.db_manager import DBManager
from models import ParsedLog, User
from utils import ParsedLogObject


class ParsedLogManager(DBManager):
    @classmethod
    def insert_parsed_logs_list(cls, normalized_logs_data: list[dict]):
        try:
            if normalized_logs_data:
                cls.insert_bulk(data_model_list=normalized_logs_data, model_class=ParsedLog)
        except Exception as e:
            logging.error(f"Error getting last entry ID: {e}")
            raise

    @classmethod
    def load_query_result(cls, row: tuple) -> ParsedLog:
        return super().load_model_query_result(model_class=ParsedLog, row=row)

    @classmethod
    def set_user_model(cls, parsed_log_object: ParsedLogObject):
        user_instance = None
        if parsed_log_object.user_id:
            with cls.reader_session() as session:
                user_instance = session.query(User).filter_by(id=parsed_log_object.user_id).first()
        parsed_log_object.user_id = getattr(user_instance, "id", None)
        parsed_log_object.user = user_instance
