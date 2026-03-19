import json
import logging
import sys
from datetime import datetime

from l4py import utils


class FormatTimeMixin:

    def format_time(self, record, datefmt=None):
        ct = datetime.fromtimestamp(record.created)
        if datefmt:
            return ct.strftime(datefmt)
        else:
            return ct.isoformat(timespec='milliseconds')


class AbstractFormatter(FormatTimeMixin, logging.Formatter):
    def __init__(self, app_name=None):
        super().__init__()
        if app_name is None:
            app_name = utils.get_app_name()
        self.app_name = app_name


class JsonFormatter(AbstractFormatter):

    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": self.format_time(record),
            "app_name": self.app_name,
            "logger_name": record.name,
            "level": record.levelname,
            "file_name": record.filename,
            "line_number": record.lineno,
            "function_name": record.funcName,
            "message": str(record.msg) % record.args,
        }
        if getattr(record, "trace_id", None):
            log_record["trace_id"] = record.trace_id
        if getattr(record, "user_id", None):
            log_record["user_id"] = record.user_id
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)
        return json.dumps(log_record, default=str)


class TextFormatter(AbstractFormatter):

    color_mapping = {
        'DEBUG': '32',
        'INFO': '34',
        'WARNING': '33',
        'ERROR': '31',
        'FATAL': '31',
        'CRITICAL': '31',
    }

    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": self.format_time(record),
            "app_name": self.app_name,
            "logger_name": record.name,
            "level": record.levelname,
            "file_name": record.filename,
            "line_number": record.lineno,
            "function_name": record.funcName,
            "message": record.getMessage(),
        }
        formatted_log = '{timestamp} [{level:<8}] {app_name} {logger_name} {file_name}:{line_number} {function_name}: {message}'.format(
            **log_record
        )
        if sys.stdout.isatty():
            formatted_log = '\033[' + self.color_mapping.get(record.levelname, '34') + f'm{formatted_log}'
        if trace_id := getattr(record, "trace_id", None):
            formatted_log += f' trace_id: {trace_id}'
        if user_id := getattr(record, "user_id", None):
            formatted_log += f' user_id: {user_id}'
        if exc_info := record.exc_info:
            formatted_log += f'\n{self.formatException(exc_info)}'
        return formatted_log + '\033[0m'
