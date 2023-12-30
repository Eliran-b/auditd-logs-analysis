import logging
import os
import re
from datetime import datetime
from config import Config
from handlers.log_handler import AuditLogHandler
from models import RawLog


class AuditLogReader(AuditLogHandler):

    def __init__(self):
        super().__init__()
        self.run_time = self._generate_run_time()
        self.last_raw_log_object: RawLog = self.raw_log_manager.get_last_raw_log_item()
        self.raw_logs_data: dict = self._load_log_files()
        self.start_line_number: int = 0

    @staticmethod
    def _generate_run_time() -> datetime:
        return datetime.utcnow()

    def _load_log_files(self) -> dict:
        log_files_data = {}
        try:
            _, start_year, start_month, file_name = self.last_raw_log_object.log_file_path.rsplit('/', maxsplit=3)
            start_year = int(start_year)
            start_month = int(start_month)
            start_day = int(file_name.split('.')[0])
            year_folders = sorted([year for year in os.listdir(Config.LOGS_FOLDER_NAME) if int(year) >= start_year])
        except AttributeError:
            start_day = 1
            start_month = 1
            year_folders = sorted([year for year in os.listdir(Config.LOGS_FOLDER_NAME)])

        # Loop through year folders
        for year_folder in year_folders:
            year_folder_path = os.path.join(Config.LOGS_FOLDER_NAME, str(year_folder))

            # Loop through month folders
            month_list = sorted([month for month in os.listdir(year_folder_path) if int(month) >= start_month])
            for month_folder in month_list:
                month_folder_path = os.path.join(year_folder_path, str(month_folder).zfill(2))

                # Loop through day files
                day_files_to_handle = sorted([day_file for day_file in os.listdir(month_folder_path) if
                                              int(day_file.split('.')[0]) >= start_day])
                for day_file in day_files_to_handle:
                    day_file_path = os.path.join(month_folder_path, day_file)

                    # Read data from the log file and append to the list
                    with open(day_file_path, 'r') as file:
                        log_files_data[day_file_path] = file.read().splitlines()

        return log_files_data

    def read_audit_logs(self):
        try:
            self._load_new_logs()
            self.raw_log_manager.insert_raw_logs_list(raw_logs_data=self.raw_logs_data,
                                                      start_line_number=self.start_line_number,
                                                      run_time=self.run_time)
        except Exception as e:
            logging.error(f"Error reading audit logs: {e}")
            raise

    def _load_new_logs(self):
        if self.last_raw_log_object:
            last_logs_file_key = self.last_raw_log_object.log_file_path
            log_content = self.raw_logs_data[last_logs_file_key][self.last_raw_log_object.line_number]
            hashed_log_content = self.raw_log_manager.generate_raw_log_hash_id(log_content)
            with self.raw_log_manager.reader_session() as session:
                raw_log_object = session.query(RawLog).filter_by(hash_id=hashed_log_content).first()

            if self.last_raw_log_object == raw_log_object:
                self.start_line_number = self.last_raw_log_object.line_number + 1
            else:
                self.start_line_number = self._get_new_logs_start_index()

    def _get_new_logs_start_index(self) -> int:
        """Implement BinarySearch to search for new logs"""
        start = 0
        end = self.last_raw_log_object.line_number
        while start <= end:
            mid = (start + end) // 2
            mid_content = self.raw_logs_data[mid]
            mid_hash_id = self.raw_log_manager.generate_raw_log_hash_id(mid_content)
            with self.raw_log_manager.reader_session() as session:
                mid_object = session.query(RawLog).filter_by(hash_id=mid_hash_id).first()

            if mid_object:
                start = mid + 1
            else:
                end = mid - 1

            if self.last_raw_log_object.hash_id == mid_hash_id:
                return start

        return 0
