import json
import logging
from datetime import datetime

from l4py import utils


class FormatTimeMixin:

    def format_time(self, record, datefmt=None):
        ct = datetime.fromtimestamp(record.created)
        if datefmt:
            return ct.strftime(datefmt)
        else:
            return ct.strftime("%Y-%m-%dT%H:%M:%S.") + f"{int(record.msecs):03d}"


class AbstractFormatter(FormatTimeMixin, logging.Formatter):
    def __init__(self, app_name=utils.get_app_name()):
        super().__init__()
        self.app_name = app_name


class JsonFormatter(AbstractFormatter):

    def format(self, record) -> str:
        log_record = {
            "timestamp": self.format_time(record),
            "app_name": self.app_name,
            "logger_name": record.name,
            "level": record.levelname,
            "file_name": record.filename,
            "line_number": record.lineno,
            "function_name": record.funcName,
            "message": record.msg,
        }
        return json.dumps(log_record)


class TextFormatter(AbstractFormatter):

    color_mapping = {
        'DEBUG': '32',
        'INFO': '34',
        'WARNING': '33',
        'FATAL': '31',
        'CRITICAL': '31',
    }

    def format(self, record) -> str:
        log_record = {
            "timestamp": self.format_time(record),
            "app_name": self.app_name,
            "logger_name": record.name,
            "level": record.levelname,
            "file_name": record.filename,
            "line_number": record.lineno,
            "function_name": record.funcName,
            "message": record.msg,
        }
        
        return '\033[' + self.color_mapping[record.levelname] + 'm{timestamp} [{level:<8}] {app_name} {file_name}:{line_number} {function_name}: {message}\033[0m'.format(
            **log_record)
