import logging
from handlers.log_handler import AuditLogHandler
from models import ParsedLog, RawLog
from utils import ParsedLogObject


class AuditLogAnalyzer(AuditLogHandler):

    def __init__(self):
        super().__init__()
        self.raw_logs_list = self.raw_log_manager.get_new_raw_logs_list()

    def analyze_audit_logs(self):
        try:
            normalized_logs_data = self._get_normalized_logs_data(raw_logs_list=self.raw_logs_list)
            self.parsed_log_manager.insert_parsed_logs_list(normalized_logs_data)
        except Exception as e:
            logging.error(f"Error analyzing logs: {e}")
            raise

    @staticmethod
    def _parse_audit_log(raw_log: RawLog) -> ParsedLogObject:
        log_string = raw_log.content
        log_dict = {"create_time": raw_log.create_time}
        default_key = "unmapped_content"

        for element in log_string.split():
            try:
                key, value = element.split('=')
                log_dict[key] = value
            except ValueError:
                log_dict[default_key] = log_dict.get(default_key, []) + [element]

        return ParsedLogObject.parse_obj(log_dict | {"data": log_dict})

    @staticmethod
    def _combine_partial_logs(parsed_log: ParsedLogObject,
                              partial_parsed_log: [ParsedLogObject, None]) -> ParsedLogObject:
        if not partial_parsed_log:
            return parsed_log
        extra_data = partial_parsed_log.data | parsed_log.data
        return ParsedLogObject.parse_obj(
             partial_parsed_log.dict(exclude={"data"}) | parsed_log.dict(exclude={"data"}) | {"data": extra_data})

    def _get_normalized_logs_data(self, raw_logs_list: list[str]) -> list[dict]:
        # Aggregate results for each rule/command
        # Return a data structure representing parsed data
        parsed_logs = []
        partial_parsed_log = None
        for log_row_data in raw_logs_list:
            raw_log = self.raw_log_manager.load_query_result(row=log_row_data)
            parsed_log = self._parse_audit_log(raw_log)
            if parsed_log.command_type or parsed_log.rule_name:
                parsed_log = self._combine_partial_logs(parsed_log, partial_parsed_log)
                self.parsed_log_manager.set_user_model(parsed_log)
                parsed_logs.append(ParsedLog(**parsed_log.dict(exclude_none=True)))
                partial_parsed_log = None
            else:
                partial_parsed_log = self._combine_partial_logs(parsed_log, partial_parsed_log)

        return parsed_logs
