from managers import RawLogManager, ParsedLogManager


class AuditLogHandler:

    def __init__(self):
        self.raw_log_manager = RawLogManager()
        self.parsed_log_manager = ParsedLogManager()
