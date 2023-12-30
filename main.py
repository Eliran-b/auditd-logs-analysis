import logging
from config import Config
from handlers import AuditLogAnalyzer, AuditLogReader

logging.basicConfig(level=logging.INFO)

Config()

if __name__ == "__main__":
    try:
        # read audit logs and store it in the raw_logs table -
        # add the creation time and the log file path of each log
        AuditLogReader().read_audit_logs()

        # query all the raw_logs that does not exist in the parsed_logs,
        # parse them and insert to parsed_logs table
        AuditLogAnalyzer().analyze_audit_logs()
    except Exception as e:
        logging.error(f"failed to run audit flow {e}")
